// App.tsx
import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, Box, Alert, Snackbar } from '@mui/material';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { InputSidebar } from './components/InputSidebar';
import { useChat } from './hooks/useChat';
import { useTheme } from './hooks/useTheme';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function AppContent() {
  const { theme, darkMode, toggleDarkMode } = useTheme();
  const {
    messages,
    isLoading,
    isStreaming,
    error,
    sessionId,
    conversations,
    sendMessage,
    clearSession,
    stopGeneration,
    loadConversation,
    deleteConversation
  } = useChat();
  
  const { isAuthenticated, error: authError } = useAuth();
  
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [inputSidebarOpen, setInputSidebarOpen] = useState(false);
  const [errorSnackbar, setErrorSnackbar] = useState<string | null>(null);
  const [input, setInput] = useState('');

  // Show error in snackbar
  React.useEffect(() => {
    if (error) {
      setErrorSnackbar(error);
    }
  }, [error]);

  React.useEffect(() => {
    if (authError) {
      setErrorSnackbar(authError);
    }
  }, [authError]);

  const handleTextSubmit = (text: string, source: 'text' | 'pdf', filename?: string) => {
    // Format the input with source information
    let formattedInput = '';
    if (source === 'pdf' && filename) {
      formattedInput = `[Document: ${filename}]\n\n${text}\n\nPlease analyze this legal document.`;
    } else {
      formattedInput = `${text}\n\nPlease analyze this legal text.`;
    }

    sendMessage(formattedInput, source, filename);
    setInputSidebarOpen(false); // Close input sidebar after submission
  };

  const handleSendMessage = async () => {
    if (input.trim()) {
      await sendMessage(input.trim());
      setInput('');
    }
  };

  const handleLoadConversation = (conversationId: string) => {
    loadConversation(conversationId);
    setSidebarOpen(false); // Close sidebar on mobile after loading
  };

  const handleDeleteConversation = (conversationId: string) => {
    deleteConversation(conversationId);
  };

  // Create state and actions objects for the ChatInterface
  const chatState = {
    messages: messages,
    input,
    loading: isLoading,
    isStreaming: isStreaming,
    sessionId: sessionId
  };

  const chatActions = {
    setInput,
    sendMessage: handleSendMessage,
    clearSession,
    stopGeneration
  };

  const inputRef = React.useRef<HTMLInputElement>(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Input Sidebar */}
        <InputSidebar
          open={inputSidebarOpen}
          onToggle={() => setInputSidebarOpen(!inputSidebarOpen)}
          onTextSubmit={handleTextSubmit}
          isProcessing={isLoading || isStreaming}
        />
        
        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0, // Important for flex children
            position: 'relative',
          }}
        >
          <ChatInterface
            state={chatState}
            actions={chatActions}
            inputRef={inputRef}
          />
        </Box>

        {/* Right Sidebar */}
        <Sidebar
          open={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          darkMode={darkMode}
          onThemeToggle={toggleDarkMode}
          sessionId={sessionId}
          onClearSession={clearSession}
          isStreaming={isStreaming}
          loading={isLoading}
          conversations={conversations}
          onLoadConversation={handleLoadConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </Box>

      {/* Error Snackbar */}
      <Snackbar
        open={!!errorSnackbar}
        autoHideDuration={6000}
        onClose={() => setErrorSnackbar(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setErrorSnackbar(null)}
          severity="error"
          variant="filled"
          sx={{ width: '100%' }}
        >
          {errorSnackbar}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
