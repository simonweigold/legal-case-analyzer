// hooks/useChat.ts
import { useState, useCallback, useMemo, useRef } from 'react';

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatState {
  messages: ChatMessage[];
  input: string;
  loading: boolean;
  isStreaming: boolean;
  sessionId: string;
}

export interface ChatActions {
  setInput: (input: string) => void;
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  sendMessage: () => Promise<void>;
  clearSession: () => Promise<void>;
  resetChat: () => void;
}

interface UseChatOptions {
  apiBase: string;
  onError?: (error: string) => void;
  onSuccess?: () => void;
}

export function useChat({ apiBase, onError, onSuccess }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID().slice(0, 8));
  
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading || isStreaming) return;
    
    setLoading(true);
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setInput("");

    // Try streaming first, fallback to regular chat if streaming fails
    try {
      setIsStreaming(true);
      
      const response = await fetch(`${apiBase}/chat/stream`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "text/event-stream"
        },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Streaming failed: ${response.status}`);
      }

      // Add an empty assistant message that we'll update as we stream
      let assistantMessageIndex: number;
      setMessages(prev => {
        const newMessages = [...prev, { role: "assistant" as const, content: "" }];
        assistantMessageIndex = newMessages.length - 1;
        return newMessages;
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";
      let hasReceivedContent = false;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.error) {
                  throw new Error(data.error);
                }
                
                if (data.type === 'token' && data.content) {
                  hasReceivedContent = true;
                  accumulatedContent += data.content;
                  setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                      role: "assistant" as const,
                      content: accumulatedContent
                    };
                    return newMessages;
                  });
                } else if (data.type === 'tool') {
                  const toolIndicator = `\n\n🔧 ${data.content}`;
                  setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                      role: "assistant" as const,
                      content: accumulatedContent + toolIndicator
                    };
                    return newMessages;
                  });
                } else if (data.type === 'tool_result') {
                  const resultIndicator = `\n\n✅ Tool completed\n\n`;
                  accumulatedContent += resultIndicator;
                  setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[assistantMessageIndex] = {
                      role: "assistant" as const,
                      content: accumulatedContent
                    };
                    return newMessages;
                  });
                } else if (data.done) {
                  break;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      }

      // If no content was received via streaming, fallback to regular chat
      if (!hasReceivedContent) {
        throw new Error('No content received from streaming');
      }

      onSuccess?.();

    } catch (streamError) {
      console.warn('Streaming failed, falling back to regular chat:', streamError);
      
      // Remove the empty assistant message if streaming failed
      setMessages(prev => prev.slice(0, -1));
      
      // Fallback to regular non-streaming API
      try {
        const res = await fetch(`${apiBase}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, session_id: sessionId }),
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        const data: { response: string; session_id: string } = await res.json();
        setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
        onSuccess?.();
      } catch (fallbackError: any) {
        const errorMessage = `Error: ${fallbackError?.message || String(fallbackError)}`;
        setMessages(prev => [...prev, { role: "assistant", content: errorMessage }]);
        onError?.(errorMessage);
      }
    } finally {
      setLoading(false);
      setIsStreaming(false);
      inputRef.current?.focus();
    }
  }, [apiBase, input, loading, isStreaming, sessionId, onError, onSuccess]);

  const clearSession = useCallback(async () => {
    if (isStreaming) return;
    try { 
      await fetch(`${apiBase}/chat/history/${sessionId}`, { method: "DELETE" }); 
    } catch {}
    setMessages([]);
    setSessionId(crypto.randomUUID().slice(0, 8));
    setInput("");
    inputRef.current?.focus();
  }, [apiBase, sessionId, isStreaming]);

  const resetChat = useCallback(() => {
    setMessages([]);
    setInput("");
    setLoading(false);
    setIsStreaming(false);
  }, []);

  const state: ChatState = {
    messages,
    input,
    loading,
    isStreaming,
    sessionId
  };

  const actions: ChatActions = {
    setInput,
    setMessages,
    sendMessage,
    clearSession,
    resetChat
  };

  return {
    state,
    actions,
    inputRef
  };
}
