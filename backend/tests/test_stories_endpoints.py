import sys
import unittest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from starlette.testclient import TestClient
from main import app


class TestStoriesEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # 1. Test Listing Stories Feed
    def test_list_stories_feed(self):
        resp = self.client.get("/api/stories?limit=10")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total", data)
        self.assertIn("stories", data)
        self.assertIsInstance(data["stories"], list)

        if data["stories"]:
            story = data["stories"][0]
            self.assertIn("id", story)
            self.assertIn("title", story)
            self.assertIn("what", story)
            self.assertIn("why_it_matters", story)
            self.assertIn("impact", story)
            self.assertIn("confidence", story)
            self.assertIn("ranking_score", story)
            self.assertIn("sources", story)
            self.assertIsInstance(story["sources"], list)

    # 2. Test Category Filtering
    def test_list_stories_category_filter(self):
        resp = self.client.get("/api/stories?category=LLMs & GenAI&limit=5")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        for s in data["stories"]:
            self.assertEqual(s["category"], "LLMs & GenAI")

    # 3. Test Sorting Options (rank, recent, confidence)
    def test_list_stories_sorting_options(self):
        # Sort by rank
        resp_rank = self.client.get("/api/stories?sort_by=rank&limit=5")
        self.assertEqual(resp_rank.status_code, 200)
        stories_rank = resp_rank.json()["stories"]
        if len(stories_rank) >= 2:
            self.assertGreaterEqual(stories_rank[0]["ranking_score"], stories_rank[1]["ranking_score"])

        # Sort by recent
        resp_recent = self.client.get("/api/stories?sort_by=recent&limit=5")
        self.assertEqual(resp_recent.status_code, 200)

        # Sort by confidence
        resp_conf = self.client.get("/api/stories?sort_by=confidence&limit=5")
        self.assertEqual(resp_conf.status_code, 200)

    # 4. Test Story Detail Endpoint with Claims & Sources
    def test_story_detail(self):
        feed_resp = self.client.get("/api/stories?limit=1")
        self.assertEqual(feed_resp.status_code, 200)
        feed_data = feed_resp.json()
        if feed_data["stories"]:
            story_id = feed_data["stories"][0]["id"]
            detail_resp = self.client.get(f"/api/stories/{story_id}")
            self.assertEqual(detail_resp.status_code, 200)
            detail = detail_resp.json()
            self.assertEqual(detail["id"], story_id)
            self.assertIn("claims", detail)
            self.assertIn("sources", detail)
            self.assertIn("timeline", detail)

    # 5. Test Story Detail 404 for Non-Existent Story
    def test_story_detail_404(self):
        resp = self.client.get("/api/stories/00000000-0000-0000-0000-000000000000")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"], "Story not found")

    # 6. Test Platform Telemetry Stats Endpoint
    def test_platform_stats(self):
        resp = self.client.get("/api/stats")
        self.assertEqual(resp.status_code, 200)
        stats = resp.json()
        self.assertIn("total_stories", stats)
        self.assertIn("verified_stories", stats)
        self.assertIn("total_claims", stats)
        self.assertIn("total_sources", stats)
        self.assertIn("average_confidence", stats)
        self.assertIn("categories", stats)
        self.assertGreater(stats["total_stories"], 0)
        self.assertGreater(stats["total_sources"], 0)


if __name__ == "__main__":
    unittest.main()
