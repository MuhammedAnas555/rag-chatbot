import { Copy } from "lucide-react";

function formatTime(isoTime) {
  const date = new Date(isoTime);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatMessage({ message, onCopy }) {
  const isUser = message.role === "user";

  return (
    <div className={`animate-fadeIn flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[90%] rounded-2xl px-4 py-3 shadow-md sm:max-w-[80%] ${
          isUser
            ? "rounded-br-sm bg-cyan-600 text-white"
            : "rounded-bl-sm border border-slate-700 bg-slate-800/80 text-slate-100"
        }`}
      >
        <p className="whitespace-pre-wrap break-words text-sm leading-relaxed sm:text-base">
          {message.text}
        </p>

        {!isUser && message.sources?.length > 0 && (
          <p className="mt-3 border-t border-slate-700/70 pt-2 text-[10px] text-slate-300">
            Sources - {message.sources.join(", ")}
          </p>
        )}

        <div className="mt-2 flex items-center justify-between gap-4 text-[11px] text-slate-300/90">
          <span>{formatTime(message.timestamp)}</span>
          {!isUser && (
            <button
              type="button"
              onClick={() => onCopy(message.text)}
              className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-slate-200 transition hover:bg-slate-700"
              aria-label="Copy answer"
            >
              <Copy size={14} />
              Copy
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
