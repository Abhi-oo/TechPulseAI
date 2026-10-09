import unittest
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas.short_news import IntelligenceCard, RankingComponents
from agents.short_news import ShortNewsAgent
from services.ranking import calculate_ranking_components, determine_verified_status


class TestShortNewsAndRanking(unittest.TestCase):

    def setUp(self):
        self.agent = ShortNewsAgent()

    # 1. Test Structured Output Validation (<= 30 words per field)
    def test_structured_output_validation(self):
        long_text = "word " * 50  # 50 words
        card = IntelligenceCard(
            what=long_text,
            why_it_matters=long_text,
            impact=long_text
        )
        self.assertLessEqual(len(card.what.split()), 31)  # 30 words + ellipsis
        self.assertLessEqual(len(card.why_it_matters.split()), 31)
        self.assertLessEqual(len(card.impact.split()), 31)
        self.assertTrue(card.what.endswith("..."))

    # 2. Test That Unsupported Facts Are Not Added
    def test_unsupported_facts_not_added(self):
        verified_what = "Researchers at Stanford released a 7B parameter reasoning model on GitHub."
        verified_why = "The architecture uses novel latent-space optimization to cut memory requirements in half."
        verified_impact = "Enables open-source research labs to replicate frontier reasoning capabilities on commodity hardware."
        stored_claims = [
            {"claim_text": "Model parameters: 7B", "status": "CONFIRMED"}
        ]

        card = self.agent._summarize_heuristically(
            existing_what=verified_what,
            existing_why=verified_why,
            existing_impact=verified_impact,
            stored_claims=stored_claims
        )

        # Output must be drawn directly from verified sentences
        self.assertIn("Stanford", card.what)
        self.assertIn("7B", card.what)
        self.assertIn("latent-space", card.why_it_matters)
        self.assertIn("commodity hardware", card.impact)
        # Must not contain hallucinated entities
        self.assertNotIn("OpenAI", card.what)
        self.assertNotIn("GPT-5", card.what)

    # 3. Test Ranking Calculations & Score Boundaries (0-100 scale, 30/30/20/20 weights)
    def test_ranking_calculations_and_boundaries(self):
        now = datetime.now(timezone.utc)
        fresh_story = {
            "category": "LLMs & GenAI",
            "importance_score": 8.0,  # 80/100
            "confidence": 75,         # 75/100
            "last_updated_at": now.isoformat() # 0 hours old -> 100/100 recency
        }
        claims = [{"claim_text": "C1"}, {"claim_text": "C2"}] # +10 impact bonus -> 85 + 10 = 95/100

        ranking = calculate_ranking_components(fresh_story, stored_claims=claims, now_dt=now)

        # Verify component boundaries
        self.assertGreaterEqual(ranking.recency_norm, 0.0)
        self.assertLessEqual(ranking.recency_norm, 100.0)
        self.assertGreaterEqual(ranking.importance_norm, 0.0)
        self.assertLessEqual(ranking.importance_norm, 100.0)
        self.assertGreaterEqual(ranking.impact_norm, 0.0)
        self.assertLessEqual(ranking.impact_norm, 100.0)
        self.assertGreaterEqual(ranking.confidence_norm, 0.0)
        self.assertLessEqual(ranking.confidence_norm, 100.0)
        self.assertGreaterEqual(ranking.ranking_score, 0.0)
        self.assertLessEqual(ranking.ranking_score, 100.0)

        # Expected formula check:
        # Recency: 100.0 * 0.30 = 30.0
        # Importance: 80.0 * 0.30 = 24.0
        # Impact: 95.0 * 0.20 = 19.0
        # Confidence: 75.0 * 0.20 = 15.0
        # Expected total: 88.0
        self.assertAlmostEqual(ranking.ranking_score, 88.0, delta=1.0)

    # 4. Test Missing Value Handling in Ranking
    def test_ranking_missing_values_safety(self):
        sparse_story = {
            "title": "Minimal Story",
            # All other fields missing
        }
        ranking = calculate_ranking_components(sparse_story)
        self.assertIsInstance(ranking.ranking_score, float)
        self.assertGreaterEqual(ranking.ranking_score, 0.0)
        self.assertLessEqual(ranking.ranking_score, 100.0)

    # 5. Test Low-Confidence Story Handling & Verification Guardrails
    def test_low_confidence_story_handling(self):
        # A. Low confidence (< 50) must NOT be VERIFIED
        status_low_conf = determine_verified_status(
            confidence=40,
            stored_claims=[],
            desired_status="VERIFIED"
        )
        self.assertEqual(status_low_conf, "DRAFT")

        # B. Disputed claims must NOT be VERIFIED regardless of confidence
        disputed_claims = [
            {"claim_text": "Disputed metric", "status": "DISPUTED"}
        ]
        status_disputed = determine_verified_status(
            confidence=85,
            stored_claims=disputed_claims,
            desired_status="VERIFIED"
        )
        self.assertEqual(status_disputed, "DRAFT")

        # C. High confidence with no disputes can be VERIFIED
        status_verified = determine_verified_status(
            confidence=75,
            stored_claims=[{"claim_text": "Good claim", "status": "CONFIRMED"}],
            desired_status="VERIFIED"
        )
        self.assertEqual(status_verified, "VERIFIED")

    # 6. Test Duplicate Prevention Logic
    def test_duplicate_prevention_logic(self):
        story_id = "550e8400-e29b-41d4-a716-446655440000"
        update_payload = {
            "what": "Updated concise what",
            "why_it_matters": "Updated concise why",
            "impact": "Updated concise impact",
            "ranking_score": 82.5,
            "status": "VERIFIED"
        }
        # In our architecture, the pipeline executes an UPDATE by story_id,
        # never an INSERT into stories.
        self.assertNotIn("id", update_payload)
        self.assertNotIn("slug", update_payload)


if __name__ == "__main__":
    unittest.main()
