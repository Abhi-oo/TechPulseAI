"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Story, PlatformStats } from "@/types/api";
import { fetchStories, fetchPlatformStats, triggerLiveScan } from "@/lib/api";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import StoryCard from "@/components/StoryCard";
import StoryDetailModal from "@/components/StoryDetailModal";
import SkeletonFeed from "@/components/SkeletonFeed";
import EmptyState from "@/components/EmptyState";
import ErrorState from "@/components/ErrorState";

export default function Home() {
  const [stories, setStories] = useState<Story[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [stats, setStats] = useState<PlatformStats | null>(null);

  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"rank" | "recent" | "confidence">("rank");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<{
    scanned: number;
    newArticles: number;
    researched: number;
  } | null>(null);

  // Load feed stories
  const loadFeed = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStories({
        category: selectedCategory,
        sortBy,
        search: searchQuery,
        limit: 30,
      });
      setStories(data.stories || []);
      setTotal(data.total || 0);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load intelligence feed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, sortBy, searchQuery]);

  // Load platform stats
  const loadStats = useCallback(async () => {
    try {
      const st = await fetchPlatformStats();
      setStats(st);
    } catch {
      // Stats failure is non-fatal for feed
    }
  }, []);

  useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // Handle triggering a live scan
  const handleRunScan = async () => {
    if (isScanning) return;
    setIsScanning(true);
    setScanResult(null);
    try {
      const res = await triggerLiveScan();
      setScanResult(res);
      // Reload feed and stats with real updated data
      await Promise.all([loadFeed(), loadStats()]);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to execute scan");
    } finally {
      setIsScanning(false);
    }
  };

  const handleResetFilters = () => {
    setSelectedCategory("all");
    setSearchQuery("");
    setSortBy("rank");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-[#070b12] dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
      {/* Top Navbar */}
      <Navbar
        stats={stats}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onRunScan={handleRunScan}
        isScanning={isScanning}
        scanResult={scanResult}
      />

      {/* Main Container */}
      <main className="mx-auto flex-1 w-full max-w-7xl px-4 py-6 sm:px-6">
        {/* Mobile Search Bar */}
        <div className="mb-4 block md:hidden">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search intelligence stories, models, chips..."
            className="w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 focus:border-cyan-500 focus:outline-none dark:border-slate-800 dark:bg-slate-900/80 dark:text-slate-200 dark:placeholder-slate-500"
          />
        </div>

        {/* Content Columns */}
        <div className="flex flex-col gap-6 md:flex-row">
          {/* Left Navigation Sidebar */}
          <Sidebar
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            sortBy={sortBy}
            onSortChange={setSortBy}
            stats={stats}
          />

          {/* Center Feed Stream */}
          <section className="flex-1 min-w-0">
            {/* Stream Header */}
            <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-3 dark:border-slate-800/80">
              <div>
                <h1 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                  {selectedCategory === "all" ? "For You Stream" : selectedCategory}
                </h1>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  {loading
                    ? "Updating live stream..."
                    : `Showing ${stories.length} canonical stories (${total} total in channel)`}
                </p>
              </div>

              {/* Sorting Pills for Mobile/Tablet */}
              <div className="flex items-center gap-1.5 text-xs font-mono">
                <span className="text-[10px] text-slate-400 dark:text-slate-500 uppercase">Sort:</span>
                <span className="rounded bg-slate-200 px-2 py-0.5 text-cyan-800 font-semibold text-[11px] dark:bg-slate-800/80 dark:text-cyan-300">
                  {sortBy === "rank" ? "Gravity Rank" : sortBy === "recent" ? "Most Recent" : "Confidence"}
                </span>
              </div>
            </div>

            {/* Feed States */}
            {loading ? (
              <SkeletonFeed />
            ) : error ? (
              <ErrorState message={error} onRetry={loadFeed} />
            ) : stories.length === 0 ? (
              <EmptyState
                category={selectedCategory}
                searchQuery={searchQuery}
                onReset={handleResetFilters}
              />
            ) : (
              <div className="space-y-4">
                {stories.map((story) => (
                  <StoryCard
                    key={story.id}
                    story={story}
                    onInspect={setSelectedStory}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Story Detail Dossier Modal */}
      <StoryDetailModal
        story={selectedStory}
        onClose={() => setSelectedStory(null)}
      />

      {/* Footer */}
      <footer className="mt-12 border-t border-slate-200 bg-white/70 py-6 text-center text-xs text-slate-500 font-mono dark:border-slate-900 dark:bg-slate-950/80 dark:text-slate-500 transition-colors duration-200">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            TechPulse AI © 2026 • Autonomous Intelligence Network
          </div>
          <div className="flex items-center gap-4 text-slate-500 dark:text-slate-400">
            <span>FastAPI Backend Active</span>
            <span>•</span>
            <span>Supabase Verified</span>
            <span>•</span>
            <span>Deterministic Scoring</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
