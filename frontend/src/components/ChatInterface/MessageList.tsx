// components/ChatInterface/MessageList.tsx
import React from 'react';
import { User, Bot, Brain } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { ChatMessage } from '../../hooks/useChat';

export interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  isStreaming: boolean;
}

interface MessageItemProps {
  message: ChatMessage;
  index: number;
}

function MessageItem({ message, index }: MessageItemProps) {
  const isUser = message.role === 'user';
  
  return (
    <div
      className={cn(
        "flex mb-6 animate-fade-in",
        isUser ? "justify-end" : "justify-start"
      )}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      {!isUser && (
        <div className="flex-shrink-0 mr-4 mt-1">
          <div className="w-8 h-8 bg-brand text-white rounded-causa flex items-center justify-center">
            <Bot className="w-4 h-4" />
          </div>
        </div>
      )}
      
      <div
        className={cn(
          "max-w-[80%] rounded-causa-lg shadow-sm",
          isUser
            ? "causa-message-bubble-user ml-12"
            : "causa-message-bubble-ai"
        )}
      >
        <div className="prose prose-sm max-w-none">
          {message.content.split('\n').map((line, i) => (
            <p key={i} className={cn(
              "m-0 text-body text-dark leading-relaxed",
              i > 0 && "mt-2"
            )}>
              {line || '\u00A0'}
            </p>
          ))}
        </div>
        
        <div className={cn(
          "text-small mt-3 opacity-70",
          isUser ? "text-dark/70" : "text-gray"
        )}>
          {message.timestamp.toLocaleTimeString()}
          {message.isStreaming && (
            <span className="ml-2 inline-flex items-center">
              <div className="w-1 h-1 bg-current rounded-full animate-pulse mr-1" />
              Analyzing...
            </span>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 ml-4 mt-1">
          <div className="w-8 h-8 bg-gray-dark text-white rounded-causa flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
        </div>
      )}
    </div>
  );
}

function LoadingMessage() {
  return (
    <div className="flex justify-start mb-6">
      <div className="flex-shrink-0 mr-4 mt-1">
        <div className="w-8 h-8 bg-brand text-white rounded-causa flex items-center justify-center">
          <Brain className="w-4 h-4 animate-pulse" />
        </div>
      </div>
      
      <div className="causa-message-bubble-ai">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-brand rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-brand rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-brand rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <span className="text-body text-gray ml-2">Analyzing legal content...</span>
        </div>
      </div>
    </div>
  );
}

export function MessageList({ messages, loading, isStreaming }: MessageListProps) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, isStreaming]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="h-full flex items-center justify-center p-8 overflow-y-auto">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 bg-brand/10 text-brand rounded-causa-lg flex items-center justify-center mx-auto mb-6">
            <Bot className="w-10 h-10" />
          </div>
          <h3 className="text-h2 text-dark mb-4">
            Welcome to CAUSA AI
          </h3>
          <p className="text-body text-gray-dark leading-relaxed">
            Your intelligent legal analysis assistant. Upload legal documents, enter case details, or ask questions about legal matters to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 space-y-0">
        <div className="max-w-4xl mx-auto">
          {messages.map((message, index) => (
            <MessageItem
              key={message.id}
              message={message}
              index={index}
            />
          ))}
          
          {loading && <LoadingMessage />}
          
          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}
