"use client";

import React from "react";
import { Story } from "@/types/api";

interface StoryCardProps {
  story: Story;
  onInspect: (story: Story) => void;
}

function formatRelativeTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSec < 60) return "just now";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    const diffDays = Math.floor(diffHr / 24);
    return `${diffDays}d ago`;
  } catch {
    return "";
  }
}

export default function StoryCard({ story, onInspect }: StoryCardProps) {
  // Confidence badge color mapping
  const confidenceColor =
    story.confidence >= 75
      ? "border-emerald-500/30 bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
      : story.confidence >= 55
      ? "border-cyan-500/30 bg-cyan-50 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-400"
      : "border-amber-500/30 bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400";

  return (
    <article className="ai-story-card group relative rounded-xl border border-slate-200/90 bg-white p-5 shadow-sm transition-all hover:border-cyan-500/40 hover:shadow-md hover:shadow-cyan-500/5 dark:border-slate-800 dark:bg-slate-900/70 dark:hover:border-slate-700 dark:hover:bg-slate-900/90">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 text-xs">
        <div className="flex items-center gap-2">
          {/* Category Pill */}
          <span className="rounded-md border border-slate-200 bg-slate-100 px-2.5 py-0.5 font-mono text-[11px] font-semibold text-slate-700 dark:border-slate-700/80 dark:bg-slate-800 dark:text-slate-300">
            {story.category}
          </span>

          {/* Status Badge */}
          <span
            className={`rounded-md border px-2 py-0.5 font-mono text-[10px] font-bold tracking-wider uppercase ${
              story.status === "VERIFIED"
                ? "border-emerald-500/30 bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
                : "border-slate-300 bg-slate-100 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400"
            }`}
          >
            {story.status}
          </span>
        </div>

        <div className="flex items-center gap-2.5 font-mono text-xs">
          {/* Confidence Meter */}
          <span
            className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 font-bold ${confidenceColor}`}
            title="Deterministic factual confidence score"
          >
            <span className="text-[10px] opacity-75">CONF:</span>
            {story.confidence}%
          </span>

          {/* Ranking Score */}
          <span
            className="rounded-md border border-slate-200 bg-slate-100 px-2 py-0.5 font-semibold text-slate-700 dark:border-slate-800 dark:bg-slate-800/60 dark:text-slate-300"
            title="Gravity rank score (Recency 30%, Importance 30%, Impact 20%, Confidence 20%)"
          >
            <span className="text-[10px] text-slate-400 dark:text-slate-500">RANK:</span>{" "}
            {story.ranking_score.toFixed(1)}
          </span>

          {/* Relative Timestamp */}
          <span className="text-slate-400 dark:text-slate-500 text-[11px]">
            {formatRelativeTime(story.last_updated_at || story.first_seen_at)}
          </span>
        </div>
      </div>

      {/* Story Title */}
      <h3
        onClick={() => onInspect(story)}
        className="cursor-pointer text-base font-bold text-slate-900 transition-colors group-hover:text-cyan-600 dark:text-slate-100 dark:group-hover:text-cyan-300 sm:text-lg leading-snug line-clamp-2"
      >
        {story.title}
      </h3>

      {/* Structured Narrative Triad Grid */}
      <div className="mt-4 grid grid-cols-1 gap-3 rounded-lg border border-slate-200/80 bg-slate-50/80 p-3.5 text-xs sm:grid-cols-3 dark:border-slate-800/80 dark:bg-slate-950/50">
        {/* WHAT */}
        <div className="border-b border-slate-200/80 pb-2.5 sm:border-b-0 sm:border-r sm:border-slate-200/80 sm:pr-3 sm:pb-0 dark:border-slate-800/60">
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 pb-1 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-500" />
            WHAT HAPPENED
          </div>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-4">
            {story.what}
          </p>
        </div>

        {/* WHY IT MATTERS */}
        <div className="border-b border-slate-200/80 pb-2.5 sm:border-b-0 sm:border-r sm:border-slate-200/80 sm:pr-3 sm:pb-0 dark:border-slate-800/60">
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400 pb-1 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            WHY IT MATTERS
          </div>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-4">
            {story.why_it_matters}
          </p>
        </div>

        {/* IMPACT */}
        <div>
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 pb-1 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            ECOSYSTEM IMPACT
          </div>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed line-clamp-4">
            {story.impact}
          </p>
        </div>
      </div>

      {/* Footer: Citations & Action */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3 text-xs dark:border-slate-800/80">
        {/* Source Links */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="font-mono text-[10px] text-slate-400 dark:text-slate-500 uppercase">
            Sources ({story.sources?.length || 0}):
          </span>
          {story.sources && story.sources.length > 0 ? (
            story.sources.map((src) => {
              let domain = "source";
              try {
                domain = new URL(src.article_url).hostname.replace("www.", "");
              } catch {
                domain = src.article_title.slice(0, 15);
              }
              return (
                <a
                  key={src.id}
                  href={src.article_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-md border border-slate-200 bg-slate-100/80 px-2 py-0.5 font-mono text-[11px] text-slate-700 transition-colors hover:border-cyan-500 hover:text-cyan-700 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-cyan-500/50 dark:hover:bg-slate-800 dark:hover:text-cyan-300"
                >
                  🔗 {domain}
                </a>
              );
            })
          ) : (
            <span className="text-[11px] text-slate-400 dark:text-slate-500 italic">
              Canonical Ingestion
            </span>
          )}
        </div>

        {/* Action Button */}
        <button
          onClick={() => onInspect(story)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-100 px-3 py-1 font-mono text-xs font-semibold text-slate-700 transition-all hover:border-cyan-500 hover:bg-cyan-50 hover:text-cyan-800 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-cyan-500/50 dark:hover:bg-cyan-500/10 dark:hover:text-cyan-300"
        >
          Inspect Dossier →
        </button>
      </div>
    </article>
  );
}
