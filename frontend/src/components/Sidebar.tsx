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
  { label: "For You", value: "all", backendKey: null, icon: "🌐" },
  { label: "AI & GenAI", value: "LLMs & GenAI", backendKey: "LLMs & GenAI", icon: "🧠" },
  { label: "Hardware", value: "Hardware & Silicon", backendKey: "Hardware & Silicon", icon: "⚡" },
  { label: "Open Source", value: "OpenSource & Frameworks", backendKey: "OpenSource & Frameworks", icon: "📦" },
  { label: "Cybersecurity", value: "AI Safety & Security", backendKey: "AI Safety & Security", icon: "🛡️" },
  { label: "Robotics", value: "Robotics & Autonomous", backendKey: "Robotics & Autonomous", icon: "🤖" },
  { label: "Cloud", value: "Cloud & Infrastructure", backendKey: "Cloud & Infrastructure", icon: "☁️" },
];

export default function Sidebar({
  selectedCategory,
  onSelectCategory,
  sortBy,
  onSortChange,
  stats,
}: SidebarProps) {
  return (
    <aside className="animate-entrance-sidebar relative w-full shrink-0 md:w-64 space-y-4 md:sticky md:top-20 z-10">
      {/* Persistent Left-Side Floating Decorative Particles */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-3 -z-10 overflow-hidden rounded-2xl"
      >
        <div className="sidebar-particle sidebar-particle-1" />
        <div className="sidebar-particle sidebar-particle-2" />
        <div className="sidebar-particle sidebar-particle-3" />
        <div className="sidebar-particle sidebar-particle-4" />
        <div className="sidebar-particle sidebar-particle-5" />
      </div>

      {/* Category Navigation */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-3.5 shadow-sm dark:border-slate-800/80 dark:bg-slate-900/60 dark:shadow-none backdrop-blur transition-colors duration-200">
        <div className="flex items-center justify-between px-2 pb-2.5">
          <h2 className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Live Channels
          </h2>
          <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 live-beacon-pulse" />
            REALTIME
          </span>
        </div>

        <nav className="flex flex-wrap gap-1 md:flex-col">
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat.value;
            const count =
              cat.backendKey && stats?.categories
                ? stats.categories[cat.backendKey] || 0
                : null;

            return (
              <button
                key={cat.value}
                onClick={() => onSelectCategory(cat.value)}
                data-active={isSelected}
                className={`channel-btn group flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium text-left ${
                  isSelected
                    ? "channel-active bg-cyan-50 border border-cyan-400/50 text-cyan-800 shadow-sm dark:bg-cyan-950/40 dark:border-cyan-500/40 dark:text-cyan-300 font-semibold"
                    : "text-slate-700 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800/60 dark:hover:text-white border border-transparent"
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <span className="text-sm transition-transform duration-150 group-hover:scale-110 group-hover:translate-x-0.5">
                    {cat.icon}
                  </span>
                  <span className="truncate">{cat.label}</span>
                </div>

                {count !== null && count > 0 && (
                  <span
                    className={`ml-2 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-mono transition-colors ${
                      isSelected
                        ? "bg-cyan-200 text-cyan-900 dark:bg-cyan-400/20 dark:text-cyan-200 font-bold"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 group-hover:bg-slate-200 dark:group-hover:bg-slate-700"
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

      {/* Stream Ordering Selector */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-3.5 shadow-sm dark:border-slate-800/80 dark:bg-slate-900/60 dark:shadow-none backdrop-blur transition-colors duration-200">
        <h2 className="px-2 pb-2 text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Stream Ordering
        </h2>
        <div className="grid grid-cols-3 gap-1 md:grid-cols-1">
          <button
            onClick={() => onSortChange("rank")}
            data-active={sortBy === "rank"}
            className={`channel-btn rounded-lg px-2.5 py-1.5 text-xs font-medium text-left ${
              sortBy === "rank"
                ? "channel-active bg-slate-100 border border-slate-300 text-cyan-700 font-semibold dark:bg-slate-800 dark:border-slate-700 dark:text-cyan-300"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-850 border border-transparent"
            }`}
          >
            ⚡ Top Gravity Rank
          </button>
          <button
            onClick={() => onSortChange("recent")}
            data-active={sortBy === "recent"}
            className={`channel-btn rounded-lg px-2.5 py-1.5 text-xs font-medium text-left ${
              sortBy === "recent"
                ? "channel-active bg-slate-100 border border-slate-300 text-cyan-700 font-semibold dark:bg-slate-800 dark:border-slate-700 dark:text-cyan-300"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-850 border border-transparent"
            }`}
          >
            🕒 Most Recent
          </button>
          <button
            onClick={() => onSortChange("confidence")}
            data-active={sortBy === "confidence"}
            className={`channel-btn rounded-lg px-2.5 py-1.5 text-xs font-medium text-left ${
              sortBy === "confidence"
                ? "channel-active bg-slate-100 border border-slate-300 text-cyan-700 font-semibold dark:bg-slate-800 dark:border-slate-700 dark:text-cyan-300"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-850 border border-transparent"
            }`}
          >
            🛡️ Highest Confidence
          </button>
        </div>
      </div>

      {/* Telemetry Footer Card */}
      {stats && (
        <div className="rounded-xl border border-slate-200/80 bg-gradient-to-b from-slate-50 to-slate-100 p-3.5 text-[11px] text-slate-600 dark:border-slate-800/60 dark:from-slate-900/40 dark:to-slate-950/60 dark:text-slate-400 shadow-sm dark:shadow-none transition-colors duration-200">
          <div className="flex items-center justify-between pb-1.5 font-mono">
            <span>Verified Stories</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">
              {stats.verified_stories}
            </span>
          </div>
          <div className="flex items-center justify-between pb-1.5 font-mono">
            <span>Active Sources</span>
            <span className="text-slate-800 dark:text-slate-200 font-bold">
              {stats.total_sources}
            </span>
          </div>
          <div className="flex items-center justify-between font-mono">
            <span>Verified Claims</span>
            <span className="text-cyan-600 dark:text-cyan-400 font-bold">
              {stats.total_claims}
            </span>
          </div>
        </div>
      )}
    </aside>
  );
}
