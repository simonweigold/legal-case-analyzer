import { useCallback, useMemo, useRef, useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export function App() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID().slice(0, 8));
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const apiBase = useMemo(() => {
    // Default to backend dev server; allow override via env at build time (Bun PUBLIC)
    return (import.meta as any).env?.BUN_PUBLIC_API_BASE || "http://localhost:8000";
  }, []);

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
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      const data: { response: string; session_id: string } = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: `Error: ${err?.message || String(err)}` },
      ]);
    } finally {
      setLoading(false);
      // refocus textarea for quick follow-up
      inputRef.current?.focus();
    }
  }, [apiBase, input, loading, sessionId]);

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearSession = async () => {
    try {
      await fetch(`${apiBase}/chat/history/${sessionId}`, { method: "DELETE" });
    } catch {}
    setMessages([]);
    setSessionId(crypto.randomUUID().slice(0, 8));
    setInput("");
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-3xl p-6">
        <header className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Case Analyzer</h1>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <span className="hidden sm:inline">Session:</span>
            <code className="rounded bg-white px-2 py-1">{sessionId}</code>
            <button
              onClick={clearSession}
              className="rounded-md border border-slate-300 bg-white px-2 py-1 text-slate-700 hover:bg-slate-100"
            >
              New
            </button>
          </div>
        </header>

        <main className="space-y-4">
          {/* Messages */}
          <div className="space-y-3">
            {messages.length === 0 && (
              <p className="text-slate-600">Ask anything about a case. Press Ctrl+Enter to send.</p>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={
                  "whitespace-pre-wrap rounded-lg border px-3 py-2 " +
                  (m.role === "user"
                    ? "border-blue-200 bg-blue-50"
                    : "border-emerald-200 bg-emerald-50")
                }
              >
                <div className="mb-1 text-xs uppercase tracking-wide text-slate-500">
                  {m.role === "user" ? "You" : "Assistant"}
                </div>
                {m.content}
              </div>
            ))}
          </div>

          {/* Composer */}
          <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={4}
              placeholder="Paste case details or ask a question..."
              className="w-full resize-y rounded-md border border-slate-200 p-2 outline-none focus:border-blue-400"
            />
            <div className="mt-2 flex items-center justify-between">
              <div className="text-xs text-slate-500">Ctrl+Enter to send</div>
              <button
                onClick={sendMessage}
                disabled={loading || input.trim().length === 0}
                className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
              >
                {loading ? (
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="4" fill="none" opacity="0.25" />
                    <path d="M22 12a10 10 0 0 1-10 10" stroke="white" strokeWidth="4" fill="none" />
                  </svg>
                ) : null}
                Send
              </button>
            </div>
          </div>

          {/* Note */}
          <p className="text-xs text-slate-500">
            Backend: <code>{apiBase}</code>
          </p>
        </main>
      </div>
    </div>
  );
}

export default App;
