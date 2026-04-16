export default function TypingIndicator() {
  return (
    <div className="animate-fadeIn rounded-2xl rounded-bl-sm border border-slate-700 bg-slate-800/70 px-4 py-3 text-sm text-slate-300 shadow-lg">
      <div className="flex items-center gap-2">
        <span>AI is thinking</span>
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.3s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:-0.15s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-cyan-300" />
        </span>
      </div>
    </div>
  );
}
