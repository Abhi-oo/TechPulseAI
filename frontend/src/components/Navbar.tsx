"use client";

import React from "react";
import { PlatformStats } from "@/types/api";

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
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Live Beacon */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 font-mono text-lg font-bold text-slate-950 shadow-lg shadow-cyan-500/20">
              TP
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-base font-extrabold tracking-tight text-white">
                  TechPulse<span className="text-cyan-400">AI</span>
                </span>
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold tracking-wider text-emerald-400">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                  LIVE
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block">
                Autonomous Technology Intelligence Network
              </p>
            </div>
          </div>
        </div>

        {/* Global Search */}
        <div className="mx-4 flex-1 max-w-md hidden md:block">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search intelligence stories, models, chips..."
              className="w-full rounded-lg border border-slate-800 bg-slate-900/80 px-3.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 transition-colors focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
            />
            {searchQuery && (
              <button
                onClick={() => onSearchChange("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Telemetry Ticker & Scan Trigger */}
        <div className="flex items-center gap-3">
          {stats && (
            <div className="hidden lg:flex items-center gap-3 border-r border-slate-800 pr-3 text-[11px] font-mono text-slate-400">
              <div>
                <span className="text-slate-500">Stories:</span>{" "}
                <span className="font-semibold text-slate-200">{stats.total_stories}</span>
              </div>
              <div>
                <span className="text-slate-500">Claims:</span>{" "}
                <span className="font-semibold text-slate-200">{stats.total_claims}</span>
              </div>
              <div>
                <span className="text-slate-500">Avg Conf:</span>{" "}
                <span className="font-semibold text-emerald-400">{stats.average_confidence}%</span>
              </div>
            </div>
          )}

          {/* Real Scan Control */}
          <button
            onClick={onRunScan}
            disabled={isScanning}
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
              isScanning
                ? "border-cyan-500/40 bg-cyan-950/30 text-cyan-300 cursor-wait"
                : "border-cyan-500/30 bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20 active:scale-95"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isScanning ? "animate-ping bg-cyan-400" : "bg-cyan-400"
              }`}
            />
            {isScanning ? "Scanning Feeds..." : "Run Intelligence Scan"}
          </button>
        </div>
      </div>

      {/* Scan Feedback Banner if active */}
      {scanResult && (
        <div className="border-t border-cyan-900/50 bg-cyan-950/40 px-4 py-1.5 text-center text-xs text-cyan-300 font-mono">
          ✓ Scan complete: {scanResult.scanned} articles scanned • {scanResult.newArticles} new items • {scanResult.researched} canonical stories updated
        </div>
      )}
    </header>
  );
}
