import React from "react";

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-rose-300 bg-rose-50/70 p-10 text-center dark:border-rose-900/40 dark:bg-rose-950/20">
      <div className="text-3xl mb-2">⚠️</div>
      <h3 className="text-base font-bold text-rose-800 dark:text-rose-300">
        Intelligence Stream Disconnected
      </h3>
      <p className="mt-1 max-w-md text-xs text-rose-600 dark:text-rose-400/80">
        {message || "Unable to reach the backend intelligence server at this time."}
      </p>
      <div className="mt-4 flex gap-3">
        <button
          onClick={onRetry}
          className="rounded-lg border border-rose-400 bg-rose-100 px-4 py-1.5 font-mono text-xs font-semibold text-rose-800 transition-colors hover:bg-rose-200 dark:border-rose-500/40 dark:bg-rose-500/20 dark:text-rose-200 dark:hover:bg-rose-500/30"
        >
          Retry Connection
        </button>
      </div>
    </div>
  );
}
