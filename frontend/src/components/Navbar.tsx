"use client";

import React from "react";
import { PlatformStats } from "@/types/api";
import { useTheme } from "@/context/ThemeContext";

interface NavbarProps {
  stats: PlatformStats | null;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onRunScan: () => void;
  isScanning: boolean;
  scanResult: { scanned: number; newArticles: number; researched: number } | null;
}

export default function Navbar({
  stats,
  searchQuery,
  onSearchChange,
  onRunScan,
  isScanning,
  scanResult,
}: NavbarProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="animate-entrance-header sticky top-0 z-30 h-16 border-b border-slate-200/80 bg-white/85 backdrop-blur-md dark:border-slate-800/80 dark:bg-slate-950/85 transition-colors duration-200">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Brand & Live Beacon */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 font-mono text-base font-bold text-slate-950 shadow-md shadow-cyan-500/20">
              TP
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
                  TechPulse<span className="text-cyan-600 dark:text-cyan-400">AI</span>
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-emerald-600 dark:text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 live-beacon-pulse" />
                  LIVE
                </span>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 hidden sm:block">
                Autonomous Technology Intelligence Network
              </p>
            </div>
          </div>
        </div>

        {/* Global Search */}
        <div className="mx-4 flex-1 max-w-md hidden md:block">
          <div className="relative">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">
              🔍
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search intelligence stories, models, chips..."
              aria-label="Search intelligence stories"
              className="w-full rounded-lg border border-slate-200 bg-slate-100/90 pl-8 pr-8 py-1.5 text-xs text-slate-800 placeholder-slate-400 transition-colors focus:border-cyan-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-cyan-500 dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-200 dark:placeholder-slate-500 dark:focus:border-cyan-400 dark:focus:bg-slate-900"
            />
            {searchQuery && (
              <button
                onClick={() => onSearchChange("")}
                aria-label="Clear search query"
                className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded p-0.5 text-xs text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-cyan-500"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Telemetry Ticker, Theme Toggle & Scan Trigger */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {stats && (
            <div className="hidden lg:flex items-center gap-3 border-r border-slate-200 dark:border-slate-800 pr-3 text-[11px] font-mono text-slate-500 dark:text-slate-400">
              <div title="Total researched canonical stories">
                <span className="text-slate-400 dark:text-slate-500">Stories:</span>{" "}
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {stats.total_stories}
                </span>
              </div>
              <div title="Total extracted and verified claims">
                <span className="text-slate-400 dark:text-slate-500">Claims:</span>{" "}
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {stats.total_claims}
                </span>
              </div>
              <div title="Average factual confidence across all canonical stories">
                <span className="text-slate-400 dark:text-slate-500">Avg Conf:</span>{" "}
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  {stats.average_confidence}%
                </span>
              </div>
            </div>
          )}

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            type="button"
            aria-label={
              theme === "dark"
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
            title={
              theme === "dark"
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-slate-100 text-slate-700 transition-all hover:border-slate-300 hover:bg-slate-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 dark:border-slate-800 dark:bg-slate-900/90 dark:text-slate-300 dark:hover:border-slate-700 dark:hover:bg-slate-850 active:scale-95"
          >
            {theme === "dark" ? (
              /* Sun icon for switching to light mode */
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-amber-400"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="m4.93 4.93 1.41 1.41" />
                <path d="m17.66 17.66 1.41 1.41" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="m6.34 17.66-1.41 1.41" />
                <path d="m19.07 4.93-1.41 1.41" />
              </svg>
            ) : (
              /* Moon icon for switching to dark mode */
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 text-slate-700"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            )}
          </button>

          {/* Real Scan Control */}
          <button
            onClick={onRunScan}
            disabled={isScanning}
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 ${
              isScanning
                ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-600 dark:bg-cyan-950/30 dark:text-cyan-300 cursor-wait"
                : "border-cyan-500/40 bg-cyan-50 text-cyan-700 hover:bg-cyan-100 hover:border-cyan-600/50 dark:border-cyan-500/30 dark:bg-cyan-500/10 dark:text-cyan-300 dark:hover:bg-cyan-500/20 active:scale-95"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isScanning
                  ? "animate-ping bg-cyan-600 dark:bg-cyan-400"
                  : "bg-cyan-600 dark:bg-cyan-400"
              }`}
            />
            <span>{isScanning ? "Scanning Feeds..." : "Run Intelligence Scan"}</span>
          </button>
        </div>
      </div>

      {/* Scan Feedback Banner if active */}
      {scanResult && (
        <div className="border-t border-cyan-200 bg-cyan-50 px-4 py-1.5 text-center text-xs text-cyan-800 font-mono dark:border-cyan-900/50 dark:bg-cyan-950/40 dark:text-cyan-300">
          ✓ Scan complete: {scanResult.scanned} articles scanned • {scanResult.newArticles} new items • {scanResult.researched} canonical stories updated
        </div>
      )}
    </header>
  );
}
