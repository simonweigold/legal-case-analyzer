// App.tsx
import React, { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { InputSidebar } from './components/InputSidebar';
import { Navbar } from './components/Navbar';
import { useChat } from './hooks/useChat';
import { useTheme } from './hooks/useTheme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { cn } from './lib/utils';

// Error Notification Component
function ErrorNotification({ error, onClose }: { error: string | null; onClose: () => void }) {
  useEffect(() => {
    if (error) {
      const timer = setTimeout(onClose, 6000);
      return () => clearTimeout(timer);
    }
  }, [error, onClose]);

  if (!error) return null;

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md w-full mx-4">
      <div className="bg-destructive text-destructive-foreground px-4 py-3 rounded-lg shadow-lg border border-destructive/20">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{error}</span>
          <button
            onClick={onClose}
            className="ml-3 text-destructive-foreground/80 hover:text-destructive-foreground"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

function AppContent() {
  const { darkMode, toggleDarkMode } = useTheme();
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
  
  const [errorSnackbar, setErrorSnackbar] = useState<string | null>(null);
  const [input, setInput] = useState('');

  // Show error in notification
  useEffect(() => {
    if (error) {
      setErrorSnackbar(error);
    }
  }, [error]);

  useEffect(() => {
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
  };

  const handleSendMessage = async () => {
    if (input.trim()) {
      await sendMessage(input.trim());
      setInput('');
    }
  };

  const handleLoadConversation = (conversationId: string) => {
    loadConversation(conversationId);
  };

  const handleDeleteConversation = (conversationId: string) => {
    deleteConversation(conversationId);
  };

  // Create state and actions objects for the ChatInterface
  const chatState = {
    messages: messages,
    input,
    isLoading: isLoading,
    loading: isLoading, // for backward compatibility
    isStreaming: isStreaming,
    sessionId: sessionId,
    error: error,
    conversationId: sessionId,
    conversations: conversations
  };

  const chatActions = {
    setInput,
    sendMessage: handleSendMessage,
    clearSession,
    stopGeneration
  };

  const inputRef = React.useRef<HTMLInputElement>(null);

  return (
    <div className={cn("h-screen", darkMode && "dark")}>
      {/* Grid layout container */}
      <div className="grid grid-cols-[auto_1fr_auto] grid-rows-[auto_1fr] h-full bg-background text-foreground">
        {/* Top navbar spanning all columns */}
        <header className="col-span-3 border-b border-border">
          <Navbar
            darkMode={darkMode}
            onThemeToggle={toggleDarkMode}
            sessionId={sessionId}
            onClearSession={clearSession}
            isStreaming={isStreaming}
            loading={isLoading}
          />
        </header>

        {/* Left sidebar - Input */}
        <aside className="border-r border-border bg-sidebar">
          <InputSidebar
            open={true}
            onToggle={() => {}}
            onTextSubmit={handleTextSubmit}
            isProcessing={isLoading || isStreaming}
          />
        </aside>

        {/* Main content area */}
        <main className="min-w-0 bg-background">
          <ChatInterface
            state={chatState}
            actions={chatActions}
            inputRef={inputRef}
          />
        </main>

        {/* Right sidebar - Conversations */}
        <aside className="border-l border-border bg-sidebar">
          <Sidebar
            open={true}
            onToggle={() => {}} 
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
        </aside>
      </div>

      {/* Error Notification */}
      <ErrorNotification
        error={errorSnackbar}
        onClose={() => setErrorSnackbar(null)}
      />
    </div>
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
