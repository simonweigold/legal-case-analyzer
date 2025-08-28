import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type React from "react";
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Chip,
  Container,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Stack,
  TextField,
  ThemeProvider,
  Toolbar,
  Tooltip,
  Typography,
  createTheme,
} from "@mui/material";
import {
  ChatRounded as ChatIcon,
  SendRounded as SendIcon,
  Brightness4Rounded as DarkIcon,
  Brightness7Rounded as LightIcon,
  RestartAltRounded as ResetIcon,
  DescriptionRounded as DocIcon,
} from "@mui/icons-material";

type ChatMessage = { role: "user" | "assistant"; content: string };

function useMuiTheme(prefersDark: boolean) {
  // Helper: read CSS var and return supported color (avoid oklch for MUI palette)
  const getVar = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim() || undefined;
  const sanitize = (value: string | undefined, fallback: string) => {
    if (!value) return fallback;
    const v = value.toLowerCase();
    if (v.includes("oklch(")) return fallback; // MUI colorManipulator doesn't support OKLCH
    return value;
  };
  const primary = sanitize(getVar("--primary"), prefersDark ? "#e5e7eb" : "#0f172a");
  const background = sanitize(getVar("--background"), prefersDark ? "#0b0b0b" : "#fafafa");
  const foreground = sanitize(getVar("--foreground"), prefersDark ? "#eeeeee" : "#111111");
  const card = sanitize(getVar("--card"), prefersDark ? "#111111" : "#ffffff");

  return createTheme({
    palette: {
      mode: prefersDark ? "dark" : "light",
  primary: { main: primary },
  background: { default: background, paper: card },
  text: { primary: foreground },
    },
    shape: { borderRadius: 10 },
    components: {
      MuiPaper: {
        styleOverrides: { root: { borderRadius: "var(--radius)" } },
      },
      MuiButton: {
        defaultProps: { variant: "contained" },
      },
    },
    typography: {
      fontFamily: "var(--font-sans)",
    },
  });
}

export function App() {
  const [dark, setDark] = useState(false);
  const theme = useMuiTheme(dark);
  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [dark]);

  const [sessionId, setSessionId] = useState(() => crypto.randomUUID().slice(0, 8));
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement | null>(null);

  const apiBase = useMemo(() => (import.meta as any).env?.BUN_PUBLIC_API_BASE || "http://localhost:8000", []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    setLoading(true);
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setInput("");
    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data: { response: string; session_id: string } = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${err?.message || String(err)}` }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [apiBase, input, loading, sessionId]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearSession = async () => {
    try { await fetch(`${apiBase}/chat/history/${sessionId}`, { method: "DELETE" }); } catch {}
    setMessages([]);
    setSessionId(crypto.randomUUID().slice(0, 8));
    setInput("");
    inputRef.current?.focus();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "flex", height: "100%" }}>
        {/* Sidebar */}
        <Drawer variant="permanent" PaperProps={{ sx: { width: 280, p: 2, borderRight: "1px solid var(--sidebar-border)", bgcolor: "var(--sidebar)" } }}>
          <Stack spacing={2} sx={{ height: "100%" }}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Avatar><ChatIcon /></Avatar>
              <Box>
                <Typography fontWeight={700}>Case Analyzer</Typography>
                <Typography variant="body2" color="text.secondary">Pitch Demo</Typography>
              </Box>
            </Stack>

            <Divider />

            <Box>
              <Typography variant="overline" color="text.secondary">Session</Typography>
              <Stack direction="row" spacing={1} alignItems="center" mt={1}>
                <Chip size="small" label={sessionId} sx={{ fontFamily: "var(--font-mono)" }} />
                <Tooltip title="New Session">
                  <IconButton color="primary" onClick={clearSession}><ResetIcon /></IconButton>
                </Tooltip>
              </Stack>
            </Box>

            <Divider />

            <Box>
              <Typography variant="overline" color="text.secondary">Value Props</Typography>
              <List>
                <ListItem>
                  <ListItemAvatar><Avatar variant="rounded"><DocIcon /></Avatar></ListItemAvatar>
                  <ListItemText primary="Analyze Decisions" secondary="Extract issues, holdings, and risk" />
                </ListItem>
                <ListItem>
                  <ListItemAvatar><Avatar variant="rounded"><DocIcon /></Avatar></ListItemAvatar>
                  <ListItemText primary="Choice of Law Issue" secondary="Identify the correct choice of law issue present in the case" />
                </ListItem>
                <ListItem>
                  <ListItemAvatar><Avatar variant="rounded"><DocIcon /></Avatar></ListItemAvatar>
                  <ListItemText primary="Court's Position" secondary="Find the Ratio Decidendi, Obiter Dicta, and Dissenting Opinions" />
                </ListItem>
              </List>
            </Box>

            <Box flexGrow={1} />

            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="caption" color="text.secondary">Backend</Typography>
              <Chip size="small" label={apiBase} sx={{ maxWidth: 160 }} />
            </Stack>
          </Stack>
        </Drawer>

        {/* Main content */}
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <AppBar position="sticky" color="transparent" elevation={0} sx={{ borderBottom: "1px solid var(--border)" }}>
            <Toolbar>
              <Typography variant="h6" sx={{ flex: 1 }}>Legal Case Conversation</Typography>
              <Tooltip title={dark ? "Switch to light" : "Switch to dark"}>
                <IconButton onClick={() => setDark(v => !v)} color="inherit">
                  {dark ? <LightIcon /> : <DarkIcon />}
                </IconButton>
              </Tooltip>
            </Toolbar>
          </AppBar>

          <Container maxWidth="md" sx={{ py: 3, flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ flex: 1, display: "flex", flexDirection: "column", gap: 1, overflowY: "auto" }}>
              {messages.length === 0 && (
                <Typography color="text.secondary">Ask anything about a case. Press Ctrl+Enter to send.</Typography>
              )}
              {messages.map((m, i) => (
                <Box key={i} sx={{
                  border: "1px solid var(--border)",
                  bgcolor: m.role === "user" ? "var(--accent)" : "var(--secondary)",
                  color: "var(--accent-foreground)",
                  p: 2,
                  borderRadius: "var(--radius)",
                }}>
                  <Typography variant="caption" sx={{ opacity: 0.75, display: "block", mb: 0.5 }}>
                    {m.role === "user" ? "You" : "Assistant"}
                  </Typography>
                  <Typography whiteSpace="pre-wrap">{m.content}</Typography>
                </Box>
              ))}
            </Box>

            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                inputRef={inputRef}
                value={input}
                onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Paste case details or ask a question..."
                multiline
                minRows={2}
                maxRows={6}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Button
                        onClick={sendMessage}
                        disabled={loading || input.trim().length === 0}
                        endIcon={<SendIcon />}
                      >
                        Send
                      </Button>
                    </InputAdornment>
                  ),
                }}
              />
            </Stack>
            <Typography variant="caption" color="text.secondary">Ctrl+Enter to send</Typography>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
