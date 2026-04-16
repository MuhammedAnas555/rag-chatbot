import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { SendHorizontal, Trash2 } from "lucide-react";
import ChatMessage from "./components/ChatMessage";
import TypingIndicator from "./components/TypingIndicator";

const API_URL = "http://localhost:8000/chat";
const STORAGE_KEY = "rag-chat-history-v1";

function loadStoredMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function createMessage(role, text, sources = []) {
  return {
    id: crypto.randomUUID(),
    role,
    text,
    sources,
    timestamp: new Date().toISOString(),
  };
}

export default function App() {
  const [messages, setMessages] = useState(loadStoredMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    const userMessage = createMessage("user", question);
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const response = await axios.post(API_URL, { question }, { timeout: 120000 });
      const { answer, sources } = response.data;
      const aiMessage = createMessage("assistant", answer, sources ?? []);
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong while contacting the backend.";
      setError(detail);
      const fallback = createMessage(
        "assistant",
        "I could not fetch an answer. Please check if backend and Ollama are running."
      );
      setMessages((prev) => [...prev, fallback]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      setError("Copy failed. Clipboard permission denied.");
    }
  };

  return (
    <main className="mx-auto flex h-screen w-full max-w-5xl flex-col p-3 sm:p-6">
      <header className="mb-3 flex items-center justify-between rounded-2xl border border-slate-700/60 bg-slate-900/60 px-4 py-3 backdrop-blur">
        <div>
          <h1 className="text-lg font-semibold text-slate-100 sm:text-xl">My AI Assistant</h1>
          <p className="text-xs text-slate-400 sm:text-sm">Ask questions from your documents</p>
        </div>
        <button
          type="button"
          onClick={handleClear}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-600 px-3 py-2 text-xs text-slate-200 transition hover:bg-slate-800 sm:text-sm"
        >
          <Trash2 size={15} />
          Clear Chat
        </button>
      </header>

      <section className="flex-1 overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-900/40 shadow-2xl backdrop-blur">
        <div className="h-full space-y-4 overflow-y-auto p-4 sm:p-5">
          {messages.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/60 p-6 text-center text-sm text-slate-400">
              Start by asking a question about your documents.
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onCopy={handleCopy} />
          ))}

          {isLoading && <TypingIndicator />}
          <div ref={chatEndRef} />
        </div>
      </section>

      {error && (
        <p className="mt-2 rounded-lg border border-rose-800 bg-rose-900/30 px-3 py-2 text-xs text-rose-200 sm:text-sm">
          {error}
        </p>
      )}

      <footer className="mt-3 rounded-2xl border border-slate-700/60 bg-slate-900/70 p-3 backdrop-blur">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Ask anything about your PDFs..."
            className="max-h-36 min-h-[44px] flex-1 resize-y rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-400 transition focus:ring-2"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="inline-flex h-11 items-center gap-2 rounded-xl bg-cyan-600 px-4 text-sm font-medium text-white transition hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <SendHorizontal size={16} />
            Send
          </button>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">Press Enter to send. Shift+Enter for new line.</p>
      </footer>
    </main>
  );
}
