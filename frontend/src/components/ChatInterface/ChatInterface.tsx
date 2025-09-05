// components/ChatInterface/ChatInterface.tsx
import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import type { ChatState, ChatActions } from '../../hooks/useChat';

export interface ChatInterfaceProps {
  state: ChatState;
  actions: ChatActions;
  inputRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | null>;
}

export function ChatInterface({ state, actions, inputRef }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages, state.loading, state.isStreaming]);

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.default'
      }}
    >
      {/* Messages Area */}
      <Box sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <MessageList 
          messages={state.messages}
          loading={state.loading}
          isStreaming={state.isStreaming}
        />
        
        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ p: 2, pt: 1 }}>
        <InputArea
          input={state.input}
          onInputChange={actions.setInput}
          onSend={actions.sendMessage}
          loading={state.loading}
          isStreaming={state.isStreaming}
          inputRef={inputRef}
        />
      </Box>
    </Box>
  );
}
