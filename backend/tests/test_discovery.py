import unittest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.discovery import DiscoveryAgent


class TestDiscoveryAgent(unittest.TestCase):
    def setUp(self):
        self.agent = DiscoveryAgent(relevance_threshold=0.4)

    def test_discovery_agent_ai_article(self):
        article = {
            "title": "OpenAI releases new reasoning model with improved benchmark scores",
            "cleaned_content": "The new model utilizes reinforcement learning and achieves state-of-the-art results on math benchmarks.",
            "url": "https://techcrunch.com/openai-reasoning"
        }
        result = self.agent.evaluate_submission(article)
        self.assertTrue(result["is_relevant"])
        self.assertEqual(result["category"], "LLMs & GenAI")
        self.assertGreaterEqual(result["relevance_score"], 0.5)

    def test_discovery_agent_hardware_article(self):
        article = {
            "title": "Nvidia announces next-gen Blackwell GPU architecture for data centers",
            "cleaned_content": "The silicon features new tensor cores and liquid cooling for extreme throughput.",
            "url": "https://arstechnica.com/nvidia-blackwell"
        }
        result = self.agent.evaluate_submission(article)
        self.assertTrue(result["is_relevant"])
        self.assertEqual(result["category"], "Hardware & Silicon")
        self.assertGreaterEqual(result["relevance_score"], 0.5)

    def test_discovery_agent_fluff_filter(self):
        article = {
            "title": "Celebrity gossip and red carpet highlights from the weekend",
            "cleaned_content": "See what stars wore on the red carpet.",
            "url": "https://example.com/celebrity"
        }
        result = self.agent.evaluate_submission(article)
        self.assertFalse(result["is_relevant"])
        self.assertEqual(result["relevance_score"], 0.0)

    def test_discovery_agent_batch_clustering(self):
        articles = [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "title": "DeepSeek unveils open-weights model v3",
                "cleaned_content": "The open source transformer model offers competitive performance on benchmarks.",
                "url": "https://venturebeat.com/deepseek-v3"
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "title": "DeepSeek open-weights model v3 benchmarks analyzed",
                "cleaned_content": "Independent researchers evaluate the open source release and performance.",
                "url": "https://techcrunch.com/deepseek-eval"
            }
        ]
        res = self.agent.run(articles)
        self.assertEqual(res["total_evaluated"], 2)
        self.assertGreaterEqual(res["candidate_stories_count"], 1)
        self.assertTrue(len(res["candidate_stories"]) > 0)
        story = res["candidate_stories"][0]
        self.assertGreaterEqual(story["relevance_score"], 0.5)


if __name__ == "__main__":
    unittest.main()
