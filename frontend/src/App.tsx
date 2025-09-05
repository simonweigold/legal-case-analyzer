import React, { useState } from "react";
import { CssBaseline, ThemeProvider, Box } from "@mui/material";
import { useTheme } from "./hooks/useTheme";
import { useChat } from "./hooks/useChat";
import { Sidebar } from "./components/Sidebar";
import { ChatInterface } from "./components/ChatInterface";
import type { AppConfig } from "./types";

const config: AppConfig = {
  apiBase: (import.meta as any).env?.BUN_PUBLIC_API_BASE || "http://localhost:8000",
  title: "Legal Case Analyzer",
  description: "AI-powered legal document analysis"
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const { theme, darkMode, toggleDarkMode } = useTheme();
  const { state, actions, inputRef } = useChat({
    apiBase: config.apiBase,
    onError: (error) => console.error('Chat error:', error),
    onSuccess: () => console.log('Message sent successfully')
  });

  const handleSidebarToggle = () => setSidebarOpen(!sidebarOpen);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* Sidebar */}
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

        {/* Main Chat Interface */}
        <Box sx={{ flexGrow: 1, ml: sidebarOpen ? 0 : 0 }}>
          <ChatInterface
            state={state}
            actions={actions}
            inputRef={inputRef}
          />
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
