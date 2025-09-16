// components/ChatInterface/ChatInterface.tsx
import React from 'react';
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
  return (
    <div className="h-full flex flex-col bg-light overflow-hidden">
      {/* Messages Area - This is the scrollable section */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <MessageList 
          messages={state.messages}
          loading={state.isLoading}
          isStreaming={state.isStreaming}
        />
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="flex-shrink-0 p-6 pt-4 border-t border-gray-dark/10">
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
