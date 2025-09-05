// components/ChatInterface/MessageList.tsx
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  Skeleton,
  Fade
} from '@mui/material';
import {
  Person,
  Psychology,
  SmartToy
} from '@mui/icons-material';
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
    <Fade in timeout={300}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          alignItems: 'flex-start'
        }}
      >
        {!isUser && (
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              mr: 2,
              mt: 0.5,
              width: 32,
              height: 32
            }}
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
