"""
Curated list of reliable technology and AI RSS sources for TechPulse AI.
Includes domains, tiers, and reliability weighting for deterministic scoring.
"""

DEFAULT_SOURCES = [
    {
        "name": "ArXiv Computer Science (AI)",
        "domain": "arxiv.org",
        "feed_url": "https://rss.arxiv.org/rss/cs.AI",
        "feed_type": "rss",
        "tier": "PRIMARY",
        "reliability_weight": 1.5,
        "is_active": True,
    },
    {
        "name": "TechCrunch AI",
        "domain": "techcrunch.com",
        "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "feed_type": "rss",
        "tier": "VERIFIED_NEWS",
        "reliability_weight": 1.2,
        "is_active": True,
    },
    {
        "name": "Ars Technica",
        "domain": "arstechnica.com",
        "feed_url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "feed_type": "rss",
        "tier": "VERIFIED_NEWS",
        "reliability_weight": 1.2,
        "is_active": True,
    },
    {
        "name": "VentureBeat AI",
        "domain": "venturebeat.com",
        "feed_url": "https://venturebeat.com/category/ai/feed/",
        "feed_type": "rss",
        "tier": "VERIFIED_NEWS",
        "reliability_weight": 1.1,
        "is_active": True,
    },
    {
        "name": "Hacker News",
        "domain": "news.ycombinator.com",
        "feed_url": "https://news.ycombinator.com/rss",
        "feed_type": "rss",
        "tier": "AGGREGATOR",
        "reliability_weight": 1.0,
        "is_active": True,
    },
    {
        "name": "The Verge (Tech)",
        "domain": "theverge.com",
        "feed_url": "https://www.theverge.com/rss/tech/index.xml",
        "feed_type": "rss",
        "tier": "VERIFIED_NEWS",
        "reliability_weight": 1.1,
        "is_active": True,
    },
]
