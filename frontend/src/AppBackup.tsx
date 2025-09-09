import React, { useState } from "react";
import { CssBaseline, ThemeProvider, Box } from "@mui/material";
import { useTheme } from "./hooks/useTheme";
import { useChat } from "./hooks/useChat";
import { Sidebar } from "./components/Sidebar";
import { InputSidebar } from "./components/InputSidebar";
import { ChatInterface } from "./components/ChatInterface";
import type { AppConfig } from "./types";

const config: AppConfig = {
  apiBase: (import.meta as any).env?.BUN_PUBLIC_API_BASE || "http://localhost:8000",
  title: "Legal Case Analyzer",
  description: "AI-powered legal document analysis"
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [inputSidebarOpen, setInputSidebarOpen] = useState(true); // Start open so you can see it
  
  const { theme, darkMode, toggleDarkMode } = useTheme();
  const { state, actions, inputRef } = useChat({
    apiBase: config.apiBase,
    onError: (error) => console.error('Chat error:', error),
    onSuccess: () => console.log('Message sent successfully')
  });

  const handleSidebarToggle = () => setSidebarOpen(!sidebarOpen);
  const handleInputSidebarToggle = () => setInputSidebarOpen(!inputSidebarOpen);

  const handleTextSubmit = (text: string, source: 'text' | 'pdf', filename?: string) => {
    // Format the input with source information
    let formattedInput = '';
    if (source === 'pdf' && filename) {
      formattedInput = `[Document: ${filename}]\n\n${text}\n\nPlease analyze this legal document.`;
    } else {
      formattedInput = `${text}\n\nPlease analyze this legal text.`;
    }

    // Set the input in the chat and trigger send
    actions.setInput(formattedInput);
    // We'll auto-send after a brief delay to allow the input to be set
    setTimeout(() => {
      actions.sendMessage();
    }, 100);
    
    // Close the input sidebar after submission
    setInputSidebarOpen(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* Input Sidebar (Left) */}
        <InputSidebar
          open={inputSidebarOpen}
          onToggle={handleInputSidebarToggle}
          onTextSubmit={handleTextSubmit}
          isProcessing={state.loading || state.isStreaming}
        />

        {/* Main Chat Interface */}
        <Box sx={{ flexGrow: 1 }}>
          <ChatInterface
            state={state}
            actions={actions}
            inputRef={inputRef}
          />
        </Box>

        {/* Conversation History Sidebar (Right) */}
        <Sidebar
          open={sidebarOpen}
          onToggle={handleSidebarToggle}
          darkMode={darkMode}
          onThemeToggle={toggleDarkMode}
          sessionId={state.sessionId}
          onClearSession={actions.clearSession}
          isStreaming={state.isStreaming}
          loading={state.loading}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
