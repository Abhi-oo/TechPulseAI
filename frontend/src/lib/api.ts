import { StoryFeedResponse, StoryDetailResponse, PlatformStats } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface FeedParams {
  category?: string;
  sortBy?: "rank" | "recent" | "confidence";
  search?: string;
  limit?: number;
  offset?: number;
}

export async function fetchStories(params: FeedParams = {}): Promise<StoryFeedResponse> {
  const url = new URL(`${API_BASE}/stories`);
  if (params.category && params.category !== "all" && params.category !== "For You") {
    url.searchParams.set("category", params.category);
  }
  if (params.sortBy) {
    url.searchParams.set("sort_by", params.sortBy);
  }
  if (params.search && params.search.trim()) {
    url.searchParams.set("search", params.search.trim());
  }
  if (params.limit) {
    url.searchParams.set("limit", params.limit.toString());
  }
  if (params.offset) {
    url.searchParams.set("offset", params.offset.toString());
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch stories (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function fetchStoryDetail(idOrSlug: string): Promise<StoryDetailResponse> {
  const res = await fetch(`${API_BASE}/stories/${encodeURIComponent(idOrSlug)}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch story details (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function fetchPlatformStats(): Promise<PlatformStats> {
  const res = await fetch(`${API_BASE}/stats`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch platform stats (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function triggerLiveScan(): Promise<{
  scanned: number;
  newArticles: number;
  researched: number;
}> {
  // Step 1: Discovery Scan
  const discRes = await fetch(`${API_BASE}/discovery/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!discRes.ok) throw new Error("Discovery scan failed");
  const discData = await discRes.json();

  // Step 2: Research & Verification
  const resRes = await fetch(`${API_BASE}/research/run?limit=10`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!resRes.ok) throw new Error("Research pass failed");
  const resData = await resRes.json();

  // Step 3: Short News & Ranking
  const snRes = await fetch(`${API_BASE}/short-news/run?limit=10`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!snRes.ok) throw new Error("Short-News pass failed");

  return {
    scanned: discData.articles_scanned || 0,
    newArticles: discData.new_articles || 0,
    researched: resData.canonical_stories_created || 0,
  };
}
