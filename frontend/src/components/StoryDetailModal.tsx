"use client";

import React, { useEffect, useState } from "react";
import { Story, StoryDetailResponse } from "@/types/api";
import { fetchStoryDetail } from "@/lib/api";

interface StoryDetailModalProps {
  story: Story | null;
  onClose: () => void;
}

export default function StoryDetailModal({ story, onClose }: StoryDetailModalProps) {
  const [detail, setDetail] = useState<StoryDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!story) {
      setDetail(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetchStoryDetail(story.id)
      .then((data) => {
        setDetail(data);
      })
      .catch((err) => {
        setError(err.message || "Failed to load story details");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [story]);

  if (!story) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-story-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm sm:p-6 transition-colors duration-200"
    >
      <div className="relative max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close dossier dialog"
          className="absolute right-4 top-4 rounded-lg border border-slate-200 bg-slate-100 p-2 text-sm text-slate-500 hover:border-slate-300 hover:text-slate-900 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400 dark:hover:border-slate-700 dark:hover:text-white transition-colors"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="pr-10">
          <div className="flex flex-wrap items-center gap-2 pb-2 text-xs">
            <span className="rounded-md border border-slate-200 bg-slate-100 px-2.5 py-0.5 font-mono text-[11px] font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
              {story.category}
            </span>
            <span
              className={`rounded-md border px-2 py-0.5 font-mono text-[10px] font-bold ${
                story.status === "VERIFIED"
                  ? "border-emerald-500/30 bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
                  : "border-slate-300 bg-slate-100 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400"
              }`}
            >
              {story.status}
            </span>
            <span className="font-mono text-cyan-600 dark:text-cyan-400 font-bold">
              CONFIDENCE: {story.confidence}%
            </span>
            <span className="font-mono text-slate-500 dark:text-slate-400">
              RANK: {story.ranking_score.toFixed(1)}/100
            </span>
          </div>

          <h2 id="modal-story-title" className="text-xl font-bold text-slate-900 dark:text-white sm:text-2xl leading-snug">
            {story.title}
          </h2>
        </div>

        {/* Narrative Triad Details */}
        <div className="mt-5 grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs sm:grid-cols-3 dark:border-slate-800 dark:bg-slate-900/60">
          <div>
            <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 pb-1">
              WHAT HAPPENED
            </div>
            <p className="text-slate-700 dark:text-slate-200 leading-relaxed">{story.what}</p>
          </div>
          <div>
            <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400 pb-1">
              WHY IT MATTERS
            </div>
            <p className="text-slate-700 dark:text-slate-200 leading-relaxed">{story.why_it_matters}</p>
          </div>
          <div>
            <div className="font-mono text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 pb-1">
              ECOSYSTEM IMPACT
            </div>
            <p className="text-slate-700 dark:text-slate-200 leading-relaxed">{story.impact}</p>
          </div>
        </div>

        {/* Loading / Error States for Dossier */}
        {loading && (
          <div className="mt-6 flex items-center justify-center py-10 font-mono text-xs text-slate-500 dark:text-slate-400">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-500 dark:border-cyan-400 border-t-transparent mr-2" />
            Loading verified evidence dossier...
          </div>
        )}

        {error && (
          <div className="mt-6 rounded-lg border border-rose-500/30 bg-rose-50 p-3 text-xs text-rose-700 dark:bg-rose-950/20 dark:text-rose-300">
            ⚠️ {error}
          </div>
        )}

        {/* Claims and Evidence Verification Section */}
        {detail && (
          <div className="mt-6 space-y-6">
            {/* Verified Claims */}
            <div>
              <h3 className="flex items-center gap-2 font-mono text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 border-b border-slate-200 dark:border-slate-800 pb-2">
                <span>🛡️ Extracted Factual Claims ({detail.claims?.length || 0})</span>
              </h3>

              {detail.claims && detail.claims.length > 0 ? (
                <div className="mt-3 space-y-3">
                  {detail.claims.map((claim, idx) => {
                    const statusColor =
                      claim.status === "CONFIRMED"
                        ? "border-emerald-500/30 bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
                        : claim.status === "DISPUTED"
                        ? "border-rose-500/30 bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-400"
                        : "border-amber-500/30 bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400";

                    return (
                      <div
                        key={claim.id || idx}
                        className="rounded-xl border border-slate-200 bg-white p-3.5 text-xs dark:border-slate-800/80 dark:bg-slate-900/40"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 pb-1.5">
                          <span className="font-semibold text-slate-900 dark:text-slate-100">
                            Claim #{idx + 1}: {claim.claim_text}
                          </span>
                          <div className="flex items-center gap-2 font-mono">
                            <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold ${statusColor}`}>
                              {claim.status}
                            </span>
                            <span className="text-[10px] text-slate-500 dark:text-slate-400">
                              Corroboration: {claim.corroboration_count} source(s)
                            </span>
                          </div>
                        </div>

                        {/* Evidence Quotes */}
                        {claim.evidence && claim.evidence.length > 0 && (
                          <div className="mt-2 space-y-1.5 border-t border-slate-100 dark:border-slate-800/60 pt-2">
                            <div className="font-mono text-[10px] text-slate-500 dark:text-slate-400 uppercase">
                              Grounding Evidence:
                            </div>
                            {claim.evidence.map((ev, evIdx) => (
                              <blockquote
                                key={evIdx}
                                className="rounded border-l-2 border-cyan-500 bg-slate-50 p-2 text-[11px] text-slate-700 italic dark:border-cyan-500/60 dark:bg-slate-950/60 dark:text-slate-300"
                              >
                                &ldquo;{ev.quote}&rdquo;
                                <span className="block mt-1 font-mono not-italic text-[10px] text-cyan-600 dark:text-cyan-400">
                                  — {ev.source_name} ({ev.stance})
                                </span>
                              </blockquote>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="mt-2 text-xs text-slate-500 italic">
                  No discrete claims recorded for this story.
                </p>
              )}
            </div>

            {/* Timeline Evolution */}
            <div>
              <h3 className="flex items-center gap-2 font-mono text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 border-b border-slate-200 dark:border-slate-800 pb-2">
                <span>⏱️ Chronological Evolution ({detail.timeline?.length || 0})</span>
              </h3>

              {detail.timeline && detail.timeline.length > 0 ? (
                <div className="mt-3 space-y-2.5">
                  {detail.timeline.map((event) => (
                    <div
                      key={event.id}
                      className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs dark:border-slate-800 dark:bg-slate-900/40"
                    >
                      <div className="flex items-center justify-between pb-1 font-mono text-[10px]">
                        <span className="font-bold text-cyan-600 dark:text-cyan-400 uppercase">
                          {event.update_type}
                        </span>
                        <span className="text-slate-500">
                          {new Date(event.occurred_at).toLocaleString()}
                        </span>
                      </div>
                      <h4 className="font-semibold text-slate-900 dark:text-slate-100">{event.headline}</h4>
                      <p className="mt-1 text-slate-700 dark:text-slate-300 text-[11px]">{event.summary}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-2 text-xs text-slate-500 italic">
                  Initial announcement stage. No subsequent timeline updates logged yet.
                </p>
              )}
            </div>

            {/* All Sources */}
            <div>
              <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 border-b border-slate-200 dark:border-slate-800 pb-2">
                🔗 Original Sources ({detail.sources?.length || 0})
              </h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {detail.sources && detail.sources.length > 0 ? (
                  detail.sources.map((src) => (
                    <a
                      key={src.id}
                      href={src.article_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded-lg border border-slate-200 bg-slate-100 px-3 py-1.5 text-xs font-mono text-slate-700 hover:border-cyan-500 hover:text-cyan-700 dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-200 dark:hover:border-cyan-500/50 dark:hover:text-cyan-300"
                    >
                      {src.article_title} ↗
                    </a>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">No source links found.</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
