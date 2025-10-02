// hooks/useChat.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { apiService, Message, Conversation } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'tool';
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  conversationId: string | null;
  conversations: Conversation[];
}

export function useChat() {
  const { isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load conversations when user is authenticated
  const loadConversations = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const convs = await apiService.getConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Clear conversations and messages when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      setConversations([]);
      setMessages([]);
      setConversationId(null);
      setError(null);
      // Cancel any ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    }
  }, [isAuthenticated]);

  // Convert API message to ChatMessage
  const convertMessage = (msg: Message): ChatMessage => ({
    id: msg.id,
    content: msg.content,
    role: msg.role,
    timestamp: new Date(msg.timestamp),
  });

  // Load messages for a conversation
  const loadConversation = useCallback(async (convId: string) => {
    if (!isAuthenticated) return;
    
    try {
      setIsLoading(true);
      const msgs = await apiService.getMessages(convId);
      setMessages(msgs.map(convertMessage));
      setConversationId(convId);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Start a new conversation
  const startNewConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    // Cancel any ongoing requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  // Clear session (alias for startNewConversation for backward compatibility)
  const clearSession = useCallback(() => {
    startNewConversation();
  }, [startNewConversation]);

  const sendMessage = useCallback(async (content: string, source: 'text' | 'pdf' = 'text', filename?: string, tools?: string[]) => {
    if (!content.trim() || isLoading || isStreaming) return;

    // Allow sending messages even when not authenticated
    // If not authenticated, messages won't be saved to conversations

    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Create user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    // Create assistant message placeholder
    const assistantMessage: ChatMessage = {
      id: crypto.randomUUID(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);

    try {
      // Try streaming first
      await apiService.sendStreamingMessage(
        {
          message: content,
          conversation_id: conversationId || undefined,
          ...(tools && tools.length > 0 && { tools })
        },
        // On chunk received
        (chunk: string) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        // On complete
        (response) => {
          setMessages(prev => {
            const updated = prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { 
                    ...msg, 
                    // Only update content if response has content, otherwise keep accumulated content
                    content: response.response && response.response.trim() ? response.response : msg.content,
                    isStreaming: false 
                  }
                : msg
            );
            return updated;
          });
          
          // Update conversation ID if this was a new conversation and user is authenticated
          if (!conversationId && response.conversation_id && isAuthenticated) {
            setConversationId(response.conversation_id);
            loadConversations(); // Refresh conversation list
          }
        },
        // On error
        (streamError) => {
          console.error('Streaming failed, falling back to regular chat:', streamError);
          
          // Fallback to regular chat
          apiService.sendMessage({
            message: content,
            conversation_id: conversationId || undefined,
            ...(tools && tools.length > 0 && { tools })
          })
          .then((data) => {
            setMessages(prev => 
              prev.map(msg => 
                msg.id === assistantMessage.id 
                  ? { ...msg, content: data.response, isStreaming: false }
                  : msg
              )
            );
            
            if (!conversationId && data.conversation_id && isAuthenticated) {
              setConversationId(data.conversation_id);
              loadConversations();
            }
          })
          .catch((fallbackError) => {
            setError(fallbackError.message || 'Failed to send message');
            setMessages(prev => prev.filter(msg => msg.id !== assistantMessage.id));
          })
          .finally(() => {
            setIsLoading(false);
            setIsStreaming(false);
          });
        }
      );

    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Request was cancelled, remove the assistant message
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessage.id));
        return;
      }
      
      setError(error.message || 'Failed to send message');
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessage.id));
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      // Mark assistant message as no longer streaming
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { ...msg, isStreaming: false }
            : msg
        )
      );
    }
  }, [conversationId, isLoading, isStreaming, isAuthenticated, loadConversations]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
      setIsLoading(false);
    }
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback(async (convId: string) => {
    if (!isAuthenticated) return;
    
    try {
      await apiService.deleteConversation(convId);
      setConversations(prev => prev.filter(c => c.id !== convId));
      
      // If we deleted the current conversation, start a new one
      if (convId === conversationId) {
        startNewConversation();
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to delete conversation');
    }
  }, [isAuthenticated, conversationId, startNewConversation]);

  // Update conversation title
  const updateConversationTitle = useCallback(async (convId: string, title: string) => {
    if (!isAuthenticated) return;
    
    try {
      const updated = await apiService.updateConversation(convId, { title });
      setConversations(prev => prev.map(c => c.id === convId ? updated : c));
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to update conversation');
    }
  }, [isAuthenticated]);

  return {
    messages,
    isLoading,
    isStreaming,
    error,
    sessionId: conversationId || null,
    conversationId,
    conversations,
    sendMessage,
    clearSession,
    stopGeneration,
    loadConversation,
    startNewConversation,
    deleteConversation,
    updateConversationTitle,
    loadConversations,
  };
}
