// components/Auth/AuthModal.tsx
import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  IconButton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

interface AuthModalProps {
  open: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

export function AuthModal({ open, onClose, initialMode = 'login' }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSuccess = () => {
    onClose();
  };

  const switchToLogin = () => setMode('login');
  const switchToRegister = () => setMode('register');

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          borderRadius: isMobile ? 0 : 2,
          minHeight: isMobile ? '100vh' : 'auto',
        }
      }}
    >
      <Box sx={{ position: 'relative' }}>
        <IconButton
          onClick={onClose}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 1,
          }}
        >
          <Close />
        </IconButton>
        
        <DialogContent sx={{ p: isMobile ? 2 : 3 }}>
          {mode === 'login' ? (
            <LoginForm
              onSwitchToRegister={switchToRegister}
              onSuccess={handleSuccess}
            />
          ) : (
            <RegisterForm
              onSwitchToLogin={switchToLogin}
              onSuccess={handleSuccess}
            />
          )}
        </DialogContent>
      </Box>
    </Dialog>
  );
}
