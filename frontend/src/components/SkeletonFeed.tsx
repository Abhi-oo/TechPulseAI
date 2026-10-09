import React from "react";

export default function SkeletonFeed() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="animate-pulse rounded-xl border border-slate-200/80 bg-white p-5 shadow-sm dark:border-slate-800/80 dark:bg-slate-900/40"
        >
          <div className="flex items-center justify-between pb-3">
            <div className="flex gap-2">
              <div className="h-4 w-20 rounded bg-slate-200 dark:bg-slate-800" />
              <div className="h-4 w-16 rounded bg-slate-200 dark:bg-slate-800" />
            </div>
            <div className="h-4 w-24 rounded bg-slate-200 dark:bg-slate-800" />
          </div>

          <div className="h-6 w-3/4 rounded bg-slate-200 dark:bg-slate-800" />

          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="h-20 rounded bg-slate-100 dark:bg-slate-800/60" />
            <div className="h-20 rounded bg-slate-100 dark:bg-slate-800/60" />
            <div className="h-20 rounded bg-slate-100 dark:bg-slate-800/60" />
          </div>

          <div className="mt-4 flex justify-between pt-3 border-t border-slate-100 dark:border-slate-800/60">
            <div className="h-4 w-32 rounded bg-slate-200 dark:bg-slate-800" />
            <div className="h-6 w-24 rounded bg-slate-200 dark:bg-slate-800" />
          </div>
        </div>
      ))}
    </div>
  );
}
