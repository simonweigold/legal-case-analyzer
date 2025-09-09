// components/ChatInterface/ChatInterface.tsx
import React, { useEffect, useRef } from 'react';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import type { ChatState } from '../../hooks/useChat';

export interface ChatActions {
  setInput: (value: string) => void;
  sendMessage: () => void;
  clearSession: () => void;
  stopGeneration: () => void;
}

export interface ChatInterfaceProps {
  state: ChatState & { input: string };
  actions: ChatActions;
  inputRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | null>;
}

export function ChatInterface({ state, actions, inputRef }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages, state.isLoading, state.isStreaming]);

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <MessageList 
          messages={state.messages}
          loading={state.isLoading}
          isStreaming={state.isStreaming}
        />
        
        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 pt-2 border-t border-border">
        <InputArea
          input={state.input}
          onInputChange={actions.setInput}
          onSend={actions.sendMessage}
          loading={state.isLoading}
          isStreaming={state.isStreaming}
          inputRef={inputRef}
        />
      </div>
    </div>
  );
}
