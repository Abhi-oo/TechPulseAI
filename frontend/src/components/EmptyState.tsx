import React from "react";

interface EmptyStateProps {
  category: string;
  searchQuery: string;
  onReset: () => void;
}

export default function EmptyState({ category, searchQuery, onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/50 p-12 text-center dark:border-slate-800 dark:bg-slate-900/30">
      <div className="text-3xl mb-3">📡</div>
      <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
        No Verified Intelligence Found
      </h3>
      <p className="mt-1 max-w-sm text-xs text-slate-500 dark:text-slate-400">
        {searchQuery
          ? `No stories matched your search "${searchQuery}".`
          : `No canonical stories currently match channel "${category}".`}
      </p>
      <button
        onClick={onReset}
        className="mt-4 rounded-lg border border-slate-300 bg-slate-100 px-4 py-1.5 font-mono text-xs font-semibold text-slate-700 hover:border-cyan-500 hover:text-cyan-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-cyan-500/50 dark:hover:text-cyan-300 transition-colors"
      >
        Reset Filters to "For You"
      </button>
    </div>
  );
}
