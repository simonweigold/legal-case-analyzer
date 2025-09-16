// components/ChatInterface/InputArea.tsx
import React, { KeyboardEvent } from 'react';
import { Send, Square } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface InputAreaProps {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  loading: boolean;
  isStreaming: boolean;
  inputRef: React.RefObject<HTMLInputElement | HTMLTextAreaElement | null>;
}

export function InputArea({
  input,
  onInputChange,
  onSend,
  loading,
  isStreaming,
  inputRef
}: InputAreaProps) {
  const canSend = input.trim() && !loading && !isStreaming;
  const isProcessing = loading || isStreaming;

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (canSend) {
        onSend();
      }
    }
  };

  const handleSendClick = () => {
    if (canSend) {
      onSend();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="relative">
        <textarea
          ref={inputRef as React.RefObject<HTMLTextAreaElement>}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={isProcessing ? "Analyzing..." : "Ask questions about legal cases, statutes, or documents..."}
          disabled={isProcessing}
          rows={1}
          className={cn(
            "causa-input w-full pr-16 min-h-[56px] max-h-[200px] resize-none text-body",
            isProcessing && "cursor-not-allowed opacity-75"
          )}
          style={{
            overflow: 'hidden',
            resize: 'none',
          }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement;
            target.style.height = 'auto';
            target.style.height = Math.min(target.scrollHeight, 200) + 'px';
          }}
        />
        
        <div className="absolute right-3 bottom-3 flex items-center space-x-2">
          {isProcessing && (
            <div className="flex items-center text-gray">
              <div className="w-4 h-4 border-2 border-brand border-t-transparent rounded-full animate-spin mr-2" />
              <span className="text-small">
                {isStreaming ? 'Analyzing...' : 'Processing...'}
              </span>
            </div>
          )}
          
          <button
            onClick={handleSendClick}
            disabled={!canSend}
            className={cn(
              "causa-btn bg-brand-gradient text-white h-10 w-10 p-0 rounded-causa",
              !canSend && "opacity-50 cursor-not-allowed"
            )}
            title={canSend ? "Send message" : "Enter a message to send"}
          >
            {isStreaming ? (
              <Square className="w-4 h-4" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
      
      <div className="flex items-center justify-between mt-3 text-small text-gray">
        <span>Press Enter to send, Shift+Enter for new line</span>
        {input.length > 0 && (
          <span className="text-gray-dark">{input.length} characters</span>
        )}
      </div>
    </div>
  );
}
