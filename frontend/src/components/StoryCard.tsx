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
      ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
      : story.confidence >= 55
      ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
      : "border-amber-500/30 bg-amber-500/10 text-amber-400";

  return (
    <article className="group relative rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-sm transition-all hover:border-slate-700 hover:bg-slate-900/90 hover:shadow-md hover:shadow-cyan-500/5">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 text-xs">
        <div className="flex items-center gap-2">
          {/* Category Pill */}
          <span className="rounded-md border border-slate-700/80 bg-slate-800 px-2.5 py-0.5 font-mono text-[11px] font-semibold text-slate-300">
            {story.category}
          </span>

          {/* Status Badge */}
          <span
            className={`rounded-md border px-2 py-0.5 font-mono text-[10px] font-bold tracking-wider uppercase ${
              story.status === "VERIFIED"
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-slate-700 bg-slate-800 text-slate-400"
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
            <span className="text-[10px] text-slate-400">CONF:</span>
            {story.confidence}%
          </span>

          {/* Ranking Score */}
          <span
            className="rounded-md border border-slate-800 bg-slate-800/60 px-2 py-0.5 text-slate-300 font-semibold"
            title="Gravity rank score (Recency 30%, Importance 30%, Impact 20%, Confidence 20%)"
          >
            <span className="text-[10px] text-slate-500">RANK:</span>{" "}
            {story.ranking_score.toFixed(1)}
          </span>

          {/* Relative Timestamp */}
          <span className="text-slate-500 text-[11px]">
            {formatRelativeTime(story.last_updated_at || story.first_seen_at)}
          </span>
        </div>
      </div>

      {/* Story Title */}
      <h3
        onClick={() => onInspect(story)}
        className="cursor-pointer text-base font-bold text-slate-100 transition-colors group-hover:text-cyan-300 sm:text-lg"
      >
        {story.title}
      </h3>

      {/* Structured Narrative Triad Grid */}
      <div className="mt-4 grid grid-cols-1 gap-3 rounded-lg border border-slate-800/80 bg-slate-950/50 p-3.5 text-xs sm:grid-cols-3">
        {/* WHAT */}
        <div className="border-b border-slate-800/60 pb-2.5 sm:border-b-0 sm:border-r sm:pr-3 sm:pb-0">
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-cyan-400 pb-1">
            • WHAT HAPPENED
          </div>
          <p className="text-slate-300 leading-relaxed">{story.what}</p>
        </div>

        {/* WHY IT MATTERS */}
        <div className="border-b border-slate-800/60 pb-2.5 sm:border-b-0 sm:border-r sm:pr-3 sm:pb-0">
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-amber-400 pb-1">
            • WHY IT MATTERS
          </div>
          <p className="text-slate-300 leading-relaxed">{story.why_it_matters}</p>
        </div>

        {/* IMPACT */}
        <div>
          <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-emerald-400 pb-1">
            • ECOSYSTEM IMPACT
          </div>
          <p className="text-slate-300 leading-relaxed">{story.impact}</p>
        </div>
      </div>

      {/* Footer: Citations & Action */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 pt-3 text-xs">
        {/* Source Links */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="font-mono text-[10px] text-slate-500 uppercase">Sources:</span>
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
                  className="rounded-md border border-slate-700/60 bg-slate-800/50 px-2 py-0.5 font-mono text-[11px] text-slate-300 transition-colors hover:border-cyan-500/50 hover:bg-slate-800 hover:text-cyan-300"
                >
                  🔗 {domain}
                </a>
              );
            })
          ) : (
            <span className="text-[11px] text-slate-500 italic">Canonical Ingestion</span>
          )}
        </div>

        {/* Action Button */}
        <button
          onClick={() => onInspect(story)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1 font-mono text-xs font-semibold text-slate-200 transition-all hover:border-cyan-500/50 hover:bg-cyan-500/10 hover:text-cyan-300"
        >
          Inspect Dossier →
        </button>
      </div>
    </article>
  );
}
