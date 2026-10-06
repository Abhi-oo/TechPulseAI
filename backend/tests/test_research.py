import unittest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schemas.research import ExtractedClaim, VerifiedClaimResult
from services.verification import verify_claim, verify_all_claims
from services.confidence import calculate_story_confidence
from agents.research import ResearchAgent


class TestResearchAndVerification(unittest.TestCase):

    def setUp(self):
        self.agent = ResearchAgent()

    # 1. Claim Extraction Test
    def test_claim_extraction(self):
        candidate_title = "OpenAI releases new reasoning model outperforming benchmarks"
        category = "LLMs & GenAI"
        articles = [
            {
                "title": candidate_title,
                "cleaned_content": "The new model achieves 92.4% on MMLU benchmarks and reduces inference latency by 40%."
            }
        ]
        narrative, claims = self.agent._extract_heuristically(candidate_title, category, articles)
        self.assertEqual(narrative.category, category)
        self.assertTrue(len(claims) >= 1)
        # Should extract sentence with benchmark metric
        claim_texts = [c.claim_text for c in claims]
        self.assertTrue(any("92.4%" in ct or "benchmark" in ct.lower() for ct in claim_texts))

    # 2. Confirmed Claim Test (>= 2 independent supporting sources, 0 contradictions)
    def test_confirmed_claim(self):
        claim = ExtractedClaim(
            claim_text="New chip architecture achieves 50% power reduction",
            claim_type="BENCHMARK",
            needed_evidence="Power reduction benchmark measurements"
        )
        articles = [
            {
                "source_name": "Ars Technica",
                "domain": "arstechnica.com",
                "url": "https://arstechnica.com/chip-power",
                "title": "Chip Architecture Review",
                "cleaned_content": "Lab testing confirms the new chip architecture achieves 50% power reduction in server workloads."
            },
            {
                "source_name": "TechCrunch",
                "domain": "techcrunch.com",
                "url": "https://techcrunch.com/chip-efficiency",
                "title": "Power Efficiency Benchmark",
                "cleaned_content": "Independent measurements show the chip architecture achieves 50% power reduction as claimed."
            }
        ]
        result = verify_claim(claim, articles)
        self.assertEqual(result.status, "CONFIRMED")
        self.assertGreaterEqual(result.corroboration_count, 2)
        self.assertEqual(len(result.evidence), 2)
        self.assertTrue(all(e.stance == "SUPPORTS" for e in result.evidence))

    # 3. Disputed Claim Test (1 supporting source, 1 contradicting source)
    def test_disputed_claim(self):
        claim = ExtractedClaim(
            claim_text="Company achieves quantum supremacy with 1000 qubit processor",
            claim_type="BENCHMARK",
            needed_evidence="Independent quantum benchmark"
        )
        articles = [
            {
                "source_name": "Tech Blog",
                "domain": "techblog.com",
                "url": "https://techblog.com/quantum-claim",
                "title": "Quantum processor announcement",
                "cleaned_content": "Company achieves quantum supremacy with 1000 qubit processor today."
            },
            {
                "source_name": "Scientific Report",
                "domain": "scientificreport.com",
                "url": "https://scientificreport.com/quantum-refutation",
                "title": "Independent analysis refutes claims",
                "cleaned_content": "Independent researchers refute the quantum supremacy claims, stating the benchmarks are flawed and unproven."
            }
        ]
        result = verify_claim(claim, articles)
        self.assertEqual(result.status, "DISPUTED")
        stances = [e.stance for e in result.evidence]
        self.assertIn("CONTRADICTS", stances)

    # 4. Unconfirmed Claim Test (only 1 source, no independent confirmation)
    def test_unconfirmed_claim(self):
        claim = ExtractedClaim(
            claim_text="Startup plans unannounced humanoid robot deployment next month",
            claim_type="ANNOUNCEMENT",
            needed_evidence="Official deployment schedule"
        )
        articles = [
            {
                "source_name": "Insider Leak",
                "domain": "insider.com",
                "url": "https://insider.com/robot-leak",
                "title": "Rumor mill",
                "cleaned_content": "Startup plans unannounced humanoid robot deployment next month according to unnamed sources."
            }
        ]
        result = verify_claim(claim, articles)
        self.assertEqual(result.status, "UNCONFIRMED")
        self.assertEqual(result.corroboration_count, 1)

    # 5. Deterministic Confidence Calculation Test
    def test_confidence_calculation(self):
        sources = [
            {"domain": "arxiv.org", "tier": "PRIMARY", "reliability_weight": 1.5},
            {"domain": "techcrunch.com", "tier": "VERIFIED_NEWS", "reliability_weight": 1.2}
        ]
        claims = [
            VerifiedClaimResult(
                claim_text="Model beats previous state-of-the-art",
                status="CONFIRMED",
                corroboration_count=2,
                evidence=[]
            )
        ]
        breakdown = calculate_story_confidence(sources, claims)
        self.assertIsInstance(breakdown.total_confidence, int)
        self.assertGreaterEqual(breakdown.total_confidence, 20)
        self.assertLessEqual(breakdown.total_confidence, 95)
        # Primary tier bonus must be awarded
        self.assertEqual(breakdown.primary_source_bonus, 20.0)
        # Explainable explanation must not be empty
        self.assertTrue("Primary Tier" in breakdown.explanation)

    # 6. Source Agreement Test (Consensus vs Dispute impact on confidence)
    def test_source_agreement(self):
        sources = [
            {"domain": "techcrunch.com", "tier": "VERIFIED_NEWS", "reliability_weight": 1.2},
            {"domain": "arstechnica.com", "tier": "VERIFIED_NEWS", "reliability_weight": 1.2}
        ]
        agreed_claims = [
            VerifiedClaimResult(claim_text="Claim A", status="CONFIRMED", corroboration_count=2, evidence=[]),
            VerifiedClaimResult(claim_text="Claim B", status="CONFIRMED", corroboration_count=2, evidence=[])
        ]
        disputed_claims = [
            VerifiedClaimResult(claim_text="Claim A", status="DISPUTED", corroboration_count=1, evidence=[]),
            VerifiedClaimResult(claim_text="Claim B", status="DISPUTED", corroboration_count=1, evidence=[])
        ]
        agreed_conf = calculate_story_confidence(sources, agreed_claims)
        disputed_conf = calculate_story_confidence(sources, disputed_claims)

        self.assertGreater(agreed_conf.total_confidence, disputed_conf.total_confidence)
        self.assertGreater(agreed_conf.agreement_score, disputed_conf.agreement_score)

    # 7. Research Failure Handling Test (Error isolation)
    def test_research_failure_handling(self):
        class MockFailingSupabase:
            def table(self, name):
                raise RuntimeError("Simulated Database Connection Failure")

        candidate = {
            "title": "Problematic Story",
            "category": "Testing",
            "submission_ids": ["non-existent-id"]
        }

        # Verify that process_and_persist_story raises cleanly so the caller can catch it
        import asyncio
        async def run_failing():
            agent = ResearchAgent()
            await agent.process_and_persist_story(candidate, MockFailingSupabase())

        with self.assertRaises(Exception):
            asyncio.run(run_failing())


if __name__ == "__main__":
    unittest.main()
