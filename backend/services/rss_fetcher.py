import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from time import mktime
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import feedparser
import httpx
from bs4 import BeautifulSoup

from database import get_supabase_client
from sources_config import DEFAULT_SOURCES

logger = logging.getLogger("techpulse.rss_fetcher")
logger.setLevel(logging.INFO)

# Tracking parameters to strip when canonicalizing URLs
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "mc_cid", "mc_eid", "source", "feed"
}


def canonicalize_url(raw_url: str) -> str:
    """Removes marketing/tracking query parameters and normalizes URL."""
    try:
        parsed = urlparse(raw_url.strip())
        query_params = parse_qsl(parsed.query, keep_blank_values=False)
        filtered_params = [(k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS]
        clean_query = urlencode(filtered_params)
        clean_path = parsed.path.rstrip("/") if parsed.path != "/" else "/"
        canonical = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.params,
            clean_query,
            ""  # remove fragment
        ))
        return canonical
    except Exception as e:
        logger.debug(f"URL canonicalization fallback: {e}")
        return raw_url.strip()


def compute_url_hash(url: str) -> str:
    """Computes SHA-256 hash of normalized URL for O(1) deduplication."""
    canonical = canonicalize_url(url)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def clean_html(raw_html: str) -> str:
    """Strips HTML tags and normalizes whitespace."""
    if not raw_html:
        return ""
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ")
        return " ".join(text.split())
    except Exception as e:
        logger.debug(f"HTML cleaning fallback: {e}")
        return raw_html.strip()


def parse_published_date(entry) -> str:
    """Extracts published timestamp from RSS entry in ISO 8601 UTC format."""
    for date_field in ["published_parsed", "updated_parsed", "created_parsed"]:
        time_struct = getattr(entry, date_field, None)
        if time_struct:
            try:
                dt = datetime.fromtimestamp(mktime(time_struct), tz=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def ensure_sources_seeded() -> dict:
    """
    Ensures default RSS sources exist in the Supabase 'sources' table.
    Returns a mapping of domain -> source record dict.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise RuntimeError("Supabase client is not configured.")

    existing_res = supabase.table("sources").select("*").execute()
    existing_by_domain = {s["domain"]: s for s in existing_res.data}

    for src in DEFAULT_SOURCES:
        domain = src["domain"]
        if domain not in existing_by_domain:
            logger.info(f"Seeding new source: {src['name']} ({domain})")
            insert_res = supabase.table("sources").insert(src).execute()
            if insert_res.data:
                existing_by_domain[domain] = insert_res.data[0]

    return existing_by_domain


async def fetch_single_feed(client: httpx.AsyncClient, source: dict) -> list[dict]:
    """Fetches and parses a single RSS feed asynchronously."""
    feed_url = source["feed_url"]
    source_id = source["id"]
    source_name = source["name"]
    articles = []

    try:
        response = await client.get(feed_url)
        response.raise_for_status()
        parsed = feedparser.parse(response.text)

        if parsed.bozo and not parsed.entries:
            logger.warning(f"Malformed feed or empty entries from {source_name}: {parsed.bozo_exception}")
            return []

        for entry in parsed.entries:
            raw_url = getattr(entry, "link", None)
            if not raw_url:
                continue

            canonical_url_str = canonicalize_url(raw_url)
            url_hash = compute_url_hash(canonical_url_str)
            title = getattr(entry, "title", "Untitled").strip()

            # Raw description / summary
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            if not summary and hasattr(entry, "content"):
                summary = entry.content[0].value if entry.content else ""

            cleaned = clean_html(summary)
            author = getattr(entry, "author", None)
            if author and len(author) > 250:
                author = author[:247] + "..."
            published_at = parse_published_date(entry)

            articles.append({
                "source_id": source_id,
                "title": title,
                "url": canonical_url_str,
                "url_hash": url_hash,
                "author": author,
                "raw_content": summary,
                "cleaned_content": cleaned,
                "published_at": published_at,
                "processed": False
            })

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {source_name} ({feed_url}): {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing {source_name}: {e}")
        raise

    return articles


async def ingest_rss_feeds() -> tuple[int, list[dict], int]:
    """
    Ingests all active RSS sources, deduplicates using url_hash, and stores
    new articles in the 'submissions' table.
    
    Returns:
        (articles_scanned, new_inserted_submissions, failed_feeds_count)
    """
    supabase = get_supabase_client()
    if not supabase:
        raise RuntimeError("Supabase client is not configured.")

    sources_map = ensure_sources_seeded()
    active_sources = [s for s in sources_map.values() if s.get("is_active", True)]

    articles_scanned = 0
    all_fetched_articles = []
    failed_feeds = 0

    headers = {
        "User-Agent": "TechPulseAI-Bot/1.0 (+https://github.com/techpulse-ai; news aggregator)"
    }

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
        tasks = [fetch_single_feed(client, src) for src in active_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for src, result in zip(active_sources, results):
            if isinstance(result, Exception):
                logger.error(f"Feed failed: {src['name']} - {result}")
                failed_feeds += 1
            else:
                articles_scanned += len(result)
                all_fetched_articles.extend(result)

    if not all_fetched_articles:
        logger.info("No articles fetched from any feed.")
        return articles_scanned, [], failed_feeds

    # Fetch existing url_hashes from submissions to deduplicate
    hashes = list({a["url_hash"] for a in all_fetched_articles})
    existing_hashes = set()

    # Query in batches of 100 to avoid URL/query size limits
    batch_size = 100
    for i in range(0, len(hashes), batch_size):
        sub_batch = hashes[i:i + batch_size]
        res = supabase.table("submissions").select("url_hash").in_("url_hash", sub_batch).execute()
        if res.data:
            existing_hashes.update(row["url_hash"] for row in res.data)

    # Filter out duplicates (both DB duplicates and in-run duplicates)
    seen_in_run = set()
    new_articles_to_insert = []
    for art in all_fetched_articles:
        h = art["url_hash"]
        if h not in existing_hashes and h not in seen_in_run:
            seen_in_run.add(h)
            new_articles_to_insert.append(art)

    logger.info(f"Ingestion scan: {articles_scanned} scanned, {len(new_articles_to_insert)} new to insert.")

    inserted_submissions = []
    if new_articles_to_insert:
        # Insert in chunks of 50
        for i in range(0, len(new_articles_to_insert), 50):
            chunk = new_articles_to_insert[i:i + 50]
            insert_res = supabase.table("submissions").insert(chunk).execute()
            if insert_res.data:
                inserted_submissions.extend(insert_res.data)

    return articles_scanned, inserted_submissions, failed_feeds
