import React from "react";

interface EmptyStateProps {
  category: string;
  searchQuery: string;
  onReset: () => void;
}

export default function EmptyState({ category, searchQuery, onReset }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center">
      <div className="text-3xl mb-3">📡</div>
      <h3 className="text-base font-bold text-slate-200">
        No Verified Intelligence Found
      </h3>
      <p className="mt-1 max-w-sm text-xs text-slate-400">
        {searchQuery
          ? `No stories matched your search "${searchQuery}".`
          : `No canonical stories currently match channel "${category}".`}
      </p>
      <button
        onClick={onReset}
        className="mt-4 rounded-lg border border-slate-700 bg-slate-800 px-4 py-1.5 font-mono text-xs text-slate-200 hover:border-cyan-500/50 hover:text-cyan-300"
      >
        Reset Filters to "For You"
      </button>
    </div>
  );
}
