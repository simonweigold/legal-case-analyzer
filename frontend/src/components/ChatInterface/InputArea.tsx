// components/ChatInterface/InputArea.tsx
import React, { KeyboardEvent } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Send,
  Stop
} from '@mui/icons-material';

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

  const handleKeyPress = (e: KeyboardEvent<HTMLDivElement>) => {
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
    <Paper
      elevation={3}
      sx={{
        p: 2,
        borderRadius: 2,
        backgroundColor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
        <TextField
          inputRef={inputRef}
          multiline
          fullWidth
          maxRows={4}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about legal cases, upload documents, or request analysis..."
          disabled={isProcessing}
          variant="outlined"
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'background.default',
              '&:hover': {
                backgroundColor: 'background.default',
              },
              '&.Mui-focused': {
                backgroundColor: 'background.default',
              }
            }
          }}
        />
        
        <Tooltip 
          title={
            isStreaming 
              ? "Stop streaming" 
              : canSend 
                ? "Send message (Enter)" 
                : "Type a message to send"
          }
        >
          <span>
            <IconButton
              onClick={handleSendClick}
              disabled={!canSend && !isStreaming}
              color="primary"
              sx={{
                minWidth: 40,
                height: 40,
                borderRadius: 1
              }}
            >
              {isProcessing ? (
                isStreaming ? (
                  <Stop />
                ) : (
                  <CircularProgress size={20} />
                )
              ) : (
                <Send />
              )}
            </IconButton>
          </span>
        </Tooltip>
      </Box>
      
      {/* Status Indicator */}
      {isProcessing && (
        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={12} />
          <Box
            component="span"
            sx={{
              fontSize: '0.75rem',
              color: 'text.secondary',
              fontStyle: 'italic'
            }}
          >
            {isStreaming ? 'Streaming response...' : 'Processing your request...'}
          </Box>
        </Box>
      )}
    </Paper>
  );
}
