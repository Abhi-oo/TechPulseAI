import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("techpulse.discovery_agent")
logger.setLevel(logging.INFO)

# AI & Tech Taxonomy keywords
TAXONOMY_KEYWORDS = {
    "LLMs & GenAI": [
        "llm", "large language model", "gpt", "transformer", "gemini", "claude",
        "openai", "deepseek", "anthropic", "mistral", "llama", "diffusion",
        "reasoning model", "generative ai", "tokens", "fine-tuning", "rag",
        "prompt", "reinforcement learning", "rlhf", "multimodal", "weights"
    ],
    "Hardware & Silicon": [
        "gpu", "nvidia", "blackwell", "tpu", "h100", "b200", "semiconductor",
        "tsmc", "arm", "qualcomm", "intel", "amd", "chips", "wafer",
        "silicon", "quantum computing", "asic", "datacenter", "cooling"
    ],
    "Robotics & Autonomous": [
        "robotics", "humanoid", "figure", "boston dynamics", "autonomous vehicle",
        "self-driving", "waymo", "robot", "actuator", "drone", "computer vision",
        "spatial computing"
    ],
    "OpenSource & Frameworks": [
        "open source", "hugging face", "open-source", "github", "pytorch",
        "tensorflow", "ollama", "vllm", "langchain", "llama.cpp", "apache",
        "mit license", "weights release", "benchmark"
    ],
    "AI Safety & Security": [
        "ai safety", "alignment", "jailbreak", "prompt injection", "cybersecurity",
        "watermark", "hallucination", "adversarial", "vulnerability", "cve",
        "guardrails", "deepfake"
    ],
    "Cloud & Infrastructure": [
        "kubernetes", "cloud", "serverless", "distributed systems", "cluster",
        "aws", "azure", "google cloud", "latency", "throughput", "infra"
    ]
}

# Negative/Fluff filters to suppress non-technology noise
EXCLUDE_TERMS = [
    "celebrity", "horoscope", "gossip", "diet", "lifestyle", "recipe",
    "sports betting", "lottery", "crypto casino", "giveaway"
]


class DiscoveryAgent:
    """
    Logical AI Discovery Agent.
    Evaluates raw submissions, filters noise, identifies high-signal
    tech/AI stories, and clusters related items into candidate stories.
    """

    def __init__(self, relevance_threshold: float = 0.45):
        self.relevance_threshold = relevance_threshold

    def evaluate_submission(self, sub: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a single submission's title and content.
        Computes relevance score, best category, and extracted key entities.
        """
        title = (sub.get("title") or "").lower()
        content = (sub.get("cleaned_content") or "").lower()
        full_text = f"{title} {content}"

        # 1. Check exclusion filter
        for exc in EXCLUDE_TERMS:
            if exc in title:
                return {
                    "is_relevant": False,
                    "relevance_score": 0.0,
                    "category": "Uncategorized",
                    "matched_keywords": []
                }

        # 2. Score across categories
        category_scores = {}
        matched_by_cat = {}

        for cat, kw_list in TAXONOMY_KEYWORDS.items():
            cat_score = 0
            matched = []
            for kw in kw_list:
                # Title matches carry 3x weight
                if re.search(r'\b' + re.escape(kw) + r'\b', title):
                    cat_score += 3.0
                    matched.append(kw)
                elif re.search(r'\b' + re.escape(kw) + r'\b', content):
                    cat_score += 1.0
                    matched.append(kw)

            if cat_score > 0:
                category_scores[cat] = cat_score
                matched_by_cat[cat] = matched

        if not category_scores:
            # Check general tech markers
            general_tech_terms = ["software", "developer", "api", "database", "python", "code", "model", "algorithm"]
            gen_matches = [t for t in general_tech_terms if t in title]
            if gen_matches:
                score = min(0.6, len(gen_matches) * 0.3)
                return {
                    "is_relevant": score >= self.relevance_threshold,
                    "relevance_score": round(score, 2),
                    "category": "Technology",
                    "matched_keywords": gen_matches
                }
            return {
                "is_relevant": False,
                "relevance_score": 0.1,
                "category": "Other",
                "matched_keywords": []
            }

        # Pick best category
        best_cat = max(category_scores, key=category_scores.get)
        raw_score = category_scores[best_cat]
        # Normalize score between 0.0 and 1.0 (capped at 1.0)
        relevance_score = min(1.0, round(raw_score / 6.0, 2))
        is_relevant = relevance_score >= self.relevance_threshold

        return {
            "is_relevant": is_relevant,
            "relevance_score": relevance_score,
            "category": best_cat,
            "matched_keywords": matched_by_cat[best_cat]
        }

    def _generate_topic_key(self, title: str, category: str) -> str:
        """Generates a normalized topic key from title for preliminary clustering."""
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
        words = [w for w in clean.split() if len(w) > 3][:5]
        return "-".join(words) if words else category.lower().replace(" ", "-")

    def run(self, submissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes Discovery analysis across a list of submissions.
        Returns structured list of candidate stories and metrics.
        """
        evaluated_candidates = []

        for sub in submissions:
            eval_res = self.evaluate_submission(sub)
            if eval_res["is_relevant"]:
                topic_key = self._generate_topic_key(sub.get("title", ""), eval_res["category"])
                evaluated_candidates.append({
                    "title": sub.get("title"),
                    "category": eval_res["category"],
                    "topic_key": topic_key,
                    "relevance_score": eval_res["relevance_score"],
                    "matched_keywords": eval_res["matched_keywords"],
                    "submission_ids": [sub.get("id")] if sub.get("id") else [],
                    "primary_url": sub.get("url"),
                    "summary": (sub.get("cleaned_content") or "")[:280]
                })

        # Group by topic_key if multiple submissions discuss the same topic
        grouped_stories: Dict[str, Dict[str, Any]] = {}
        for cand in evaluated_candidates:
            tkey = cand["topic_key"]
            if tkey not in grouped_stories:
                grouped_stories[tkey] = cand
            else:
                existing = grouped_stories[tkey]
                existing["submission_ids"].extend(cand["submission_ids"])
                # Take highest relevance score
                existing["relevance_score"] = max(existing["relevance_score"], cand["relevance_score"])
                # Merge matched keywords
                merged_kw = list(set(existing["matched_keywords"] + cand["matched_keywords"]))
                existing["matched_keywords"] = merged_kw

        candidate_stories = list(grouped_stories.values())

        # Sort candidate stories by relevance score descending
        candidate_stories.sort(key=lambda s: s["relevance_score"], reverse=True)

        logger.info(f"Discovery Agent evaluated {len(submissions)} articles -> {len(candidate_stories)} candidate stories")

        return {
            "total_evaluated": len(submissions),
            "candidate_stories_count": len(candidate_stories),
            "candidate_stories": candidate_stories
        }
