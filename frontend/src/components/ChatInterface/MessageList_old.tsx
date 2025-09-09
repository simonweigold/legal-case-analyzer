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
        <div className="flex-shrink-0 mr-3 mt-1">
          <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4" />
          </div>
        </div>
      )}
      
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3 shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground ml-12"
            : "bg-card text-card-foreground border border-border"
        )}
      >
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {message.content.split('\n').map((line, i) => (
            <p key={i} className={cn(
              "m-0",
              i > 0 && "mt-2"
            )}>
              {line || '\u00A0'}
            </p>
          ))}
        </div>
        
        <div className={cn(
          "text-xs mt-2 opacity-70",
          isUser ? "text-primary-foreground/70" : "text-muted-foreground"
        )}>
          {message.timestamp.toLocaleTimeString()}
          {message.isStreaming && (
            <span className="ml-2 inline-flex items-center">
              <div className="w-1 h-1 bg-current rounded-full animate-pulse mr-1" />
              Streaming...
            </span>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 ml-3 mt-1">
          <div className="w-8 h-8 bg-secondary text-secondary-foreground rounded-full flex items-center justify-center">
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
      <div className="flex-shrink-0 mr-3 mt-1">
        <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center">
          <Brain className="w-4 h-4 animate-pulse" />
        </div>
      </div>
      
      <div className="bg-card text-card-foreground border border-border rounded-lg px-4 py-3 shadow-sm">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <span className="text-sm text-muted-foreground ml-2">Analyzing...</span>
        </div>
      </div>
    </div>
  );
}

export function MessageList({ messages, loading, isStreaming }: MessageListProps) {
  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Welcome to Legal Analyzer
          </h3>
          <p className="text-muted-foreground">
            Start by uploading a legal document or asking a question about legal matters.
            I'm here to help analyze cases, contracts, and legal texts.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-0">
      <div className="max-w-4xl mx-auto">
        {messages.map((message, index) => (
          <MessageItem
            key={message.id}
            message={message}
            index={index}
          />
        ))}
        
        {loading && <LoadingMessage />}
      </div>
    </div>
  );
}
          >
            <SmartToy fontSize="small" />
          </Avatar>
        )}
        
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '75%',
            backgroundColor: isUser 
              ? 'primary.main' 
              : 'background.paper',
            color: isUser 
              ? 'primary.contrastText' 
              : 'text.primary',
            borderRadius: 2,
            ...(isUser && {
              borderBottomRightRadius: 8
            }),
            ...(!isUser && {
              borderBottomLeftRadius: 8
            })
          }}
        >
          <Typography 
            variant="body1" 
            sx={{ 
              whiteSpace: 'pre-wrap',
              lineHeight: 1.6,
              fontSize: '0.875rem'
            }}
          >
            {message.content}
          </Typography>
        </Paper>

        {isUser && (
          <Avatar
            sx={{
              bgcolor: 'secondary.main',
              ml: 2,
              mt: 0.5,
              width: 32,
              height: 32
            }}
          >
            <Person fontSize="small" />
          </Avatar>
        )}
      </Box>
    </Fade>
  );
}

function LoadingSkeleton() {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-start',
        mb: 2,
        alignItems: 'flex-start'
      }}
    >
      <Avatar
        sx={{
          bgcolor: 'primary.main',
          mr: 2,
          mt: 0.5,
          width: 32,
          height: 32
        }}
      >
        <Psychology fontSize="small" />
      </Avatar>
      
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '75%',
          backgroundColor: 'background.paper',
          borderRadius: 2,
          borderBottomLeftRadius: 8
        }}
      >
        <Skeleton variant="text" width="80%" />
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="90%" />
      </Paper>
    </Box>
  );
}

export function MessageList({ messages, loading, isStreaming }: MessageListProps) {
  return (
    <Box
      sx={{
        flexGrow: 1,
        overflowY: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {messages.length === 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            flexGrow: 1,
            textAlign: 'center',
            opacity: 0.6
          }}
        >
          <SmartToy sx={{ fontSize: 64, mb: 2, color: 'primary.main' }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Legal Case Analyzer
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
            Start a conversation to analyze legal cases, extract key information, 
            and get insights powered by AI. Upload documents or ask questions about legal matters.
          </Typography>
        </Box>
      ) : (
        <>
          {messages.map((message, index) => (
            <MessageItem key={index} message={message} index={index} />
          ))}
          
          {(loading || isStreaming) && <LoadingSkeleton />}
        </>
      )}
    </Box>
  );
}
