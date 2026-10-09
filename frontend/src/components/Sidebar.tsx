"use client";

import React from "react";
import { PlatformStats } from "@/types/api";

interface SidebarProps {
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  sortBy: "rank" | "recent" | "confidence";
  onSortChange: (sort: "rank" | "recent" | "confidence") => void;
  stats: PlatformStats | null;
}

const CATEGORIES = [
  { label: "For You", value: "all", backendKey: null },
  { label: "AI & GenAI", value: "LLMs & GenAI", backendKey: "LLMs & GenAI" },
  { label: "Hardware", value: "Hardware & Silicon", backendKey: "Hardware & Silicon" },
  { label: "Open Source", value: "OpenSource & Frameworks", backendKey: "OpenSource & Frameworks" },
  { label: "Cybersecurity", value: "AI Safety & Security", backendKey: "AI Safety & Security" },
  { label: "Robotics", value: "Robotics & Autonomous", backendKey: "Robotics & Autonomous" },
  { label: "Cloud", value: "Cloud & Infrastructure", backendKey: "Cloud & Infrastructure" },
];

export default function Sidebar({
  selectedCategory,
  onSelectCategory,
  sortBy,
  onSortChange,
  stats,
}: SidebarProps) {
  return (
    <aside className="w-full shrink-0 md:w-60">
      {/* Category Navigation */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 shadow-sm backdrop-blur">
        <h2 className="px-2 pb-2 text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400">
          Intelligence Channels
        </h2>
        <nav className="flex flex-wrap gap-1 md:flex-col">
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat.value;
            const count = cat.backendKey && stats?.categories
              ? stats.categories[cat.backendKey] || 0
              : null;

            return (
              <button
                key={cat.value}
                onClick={() => onSelectCategory(cat.value)}
                className={`flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                  isSelected
                    ? "bg-cyan-500/15 text-cyan-300 font-semibold border border-cyan-500/30 shadow-sm"
                    : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                }`}
              >
                <span>{cat.label}</span>
                {count !== null && count > 0 && (
                  <span
                    className={`ml-2 rounded-full px-1.5 py-0.2 text-[10px] font-mono ${
                      isSelected
                        ? "bg-cyan-400/20 text-cyan-200"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Sort By Selector */}
      <div className="mt-3 rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 shadow-sm backdrop-blur">
        <h2 className="px-2 pb-2 text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-400">
          Stream Ordering
        </h2>
        <div className="grid grid-cols-3 gap-1 md:grid-cols-1">
          <button
            onClick={() => onSortChange("rank")}
            className={`rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition-all ${
              sortBy === "rank"
                ? "bg-slate-800 text-cyan-300 font-semibold border border-slate-700"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            ⚡ Top Gravity Rank
          </button>
          <button
            onClick={() => onSortChange("recent")}
            className={`rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition-all ${
              sortBy === "recent"
                ? "bg-slate-800 text-cyan-300 font-semibold border border-slate-700"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            🕒 Most Recent
          </button>
          <button
            onClick={() => onSortChange("confidence")}
            className={`rounded-lg px-2.5 py-1.5 text-xs font-medium text-left transition-all ${
              sortBy === "confidence"
                ? "bg-slate-800 text-cyan-300 font-semibold border border-slate-700"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            🛡️ Highest Confidence
          </button>
        </div>
      </div>

      {/* Telemetry Footer Card */}
      {stats && (
        <div className="mt-3 rounded-xl border border-slate-800/60 bg-gradient-to-b from-slate-900/40 to-slate-950/60 p-3 text-[11px] text-slate-400">
          <div className="flex items-center justify-between pb-1 font-mono">
            <span>Verified Stories</span>
            <span className="text-emerald-400 font-semibold">{stats.verified_stories}</span>
          </div>
          <div className="flex items-center justify-between pb-1 font-mono">
            <span>Active Sources</span>
            <span className="text-slate-200 font-semibold">{stats.total_sources}</span>
          </div>
          <div className="flex items-center justify-between font-mono">
            <span>Verified Claims</span>
            <span className="text-cyan-400 font-semibold">{stats.total_claims}</span>
          </div>
        </div>
      )}
    </aside>
  );
}
