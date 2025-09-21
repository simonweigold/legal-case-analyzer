// components/ChatInterface/ChatInterface.tsx
import React from 'react';
import { Textarea } from '../ui/textarea';
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
    <div className="flex-1 flex flex-col">
      {/* Messages area - scrollable */}
      <div className="flex-1 overflow-y-auto p-8 pb-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {state.messages.length === 0 && !state.isLoading ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
              <div className="space-y-4">
                <h1 className="h1 text-4xl mb-4">Welcome to CAUSA AI</h1>
                <p className="text-lg text-muted-foreground leading-relaxed max-w-md">
                  Start by uploading a legal case or asking a question
                  about legal matters. I'm here to analyze cases and
                  help you understand them better.
                </p>
              </div>
            </div>
          ) : (
            <>
              {state.messages.map((message, index) => (
                <div key={index}>
                  {message.role === 'user' && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <p className="leading-relaxed">{message.content}</p>
                    </div>
                  )}
                  {message.role === 'assistant' && (
                    <div className="space-y-4">
                      <p className="leading-relaxed">{message.content}</p>
                    </div>
                  )}
                </div>
              ))}

              {state.isLoading && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <p className="leading-relaxed">Analyzing your request...</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Fixed input area at bottom */}
      <div className="flex-shrink-0 p-8 pt-4 border-t border-border bg-background">
        <div className="max-w-4xl mx-auto">
          <Textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            placeholder="Enter your analysis or questions here..."
            value={state.input}
            onChange={(e) => actions.setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (state.input.trim() && !state.isLoading && !state.isStreaming) {
                  actions.sendMessage();
                }
              }
            }}
            className="min-h-[150px] resize-none flowing-blue-bg flowing-blue-border focus:border-blue-400 focus:ring-2 focus:ring-blue-200 focus:ring-offset-2 transition-all duration-200"
            disabled={state.isLoading || state.isStreaming}
          />
        </div>
      </div>
    </div>
  );
}
