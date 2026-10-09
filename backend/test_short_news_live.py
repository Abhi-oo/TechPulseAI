import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from main import app
from database import get_supabase_client


def run_live_short_news_and_ranking_test():
    print("=" * 65)
    print("TECHPULSE AI: MILESTONE 4 LIVE INTEGRATION TEST")
    print("=" * 65)

    client = TestClient(app)
    supabase = get_supabase_client()

    # 1. Count stories before running to verify duplicate prevention
    count_before = supabase.table("stories").select("count", count="exact").execute().count
    print(f"\n[1/4] Supabase 'stories' row count before run: {count_before}")

    # 2. Trigger POST /api/short-news/run
    print("\n[2/4] Triggering POST /api/short-news/run?limit=10...")
    response = client.post("/api/short-news/run?limit=10")

    print(f"HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response Error: {response.text}")
        sys.exit(1)

    data = response.json()
    print("\n[3/4] Validating Pipeline Response:")
    print(f"  • Stories processed:      {data.get('stories_processed')}")
    print(f"  • Stories updated:        {data.get('stories_updated')}")
    print(f"  • Average ranking score:  {data.get('average_ranking_score')}/100")
    print(f"  • Failed stories count:   {len(data.get('failed_stories', []))}")

    assert data.get("stories_updated", 0) > 0, "No stories were updated!"
    assert data.get("average_ranking_score", 0.0) > 0.0, "Average ranking score is 0.0!"

    sample = data["results"][0]
    what_len = len(sample["what"].split())
    why_len = len(sample["why_it_matters"].split())
    impact_len = len(sample["impact"].split())

    print(f"\nSample Intelligence Card (Story ID: {sample['story_id']}):")
    print(f"  • Title:          {sample['title']}")
    print(f"  • Category:       {sample['category']}")
    print(f"  • WHAT ({what_len} words):")
    print(f"    \"{sample['what']}\"")
    print(f"  • WHY IT MATTERS ({why_len} words):")
    print(f"    \"{sample['why_it_matters']}\"")
    print(f"  • IMPACT ({impact_len} words):")
    print(f"    \"{sample['impact']}\"")
    print(f"  • Confidence:     {sample['confidence']}%")
    print(f"  • Ranking Score:  {sample['ranking_score']}/100")
    print(f"  • Status:         {sample['status']}")

    assert what_len <= 31, f"what exceeded 30 words: {what_len}"
    assert why_len <= 31, f"why_it_matters exceeded 30 words: {why_len}"
    assert impact_len <= 31, f"impact exceeded 30 words: {impact_len}"

    # 4. Verify Supabase Persistence & Zero Duplicates
    print("\n[4/4] Verifying Supabase Persistence & Duplicate Prevention:")
    count_after = supabase.table("stories").select("count", count="exact").execute().count
    print(f"  • Stories count after run: {count_after}")
    assert count_before == count_after, f"Duplicate story records detected! Before: {count_before}, After: {count_after}"
    print("  • DUPLICATE PREVENTION VERIFIED: Exact same row count preserved.")

    # Check updated fields in Supabase for sample story
    story_db = supabase.table("stories").select("*").eq("id", sample["story_id"]).execute().data[0]
    assert story_db["ranking_score"] == sample["ranking_score"], "Ranking score in DB does not match response!"
    assert story_db["what"] == sample["what"], "WHAT field in DB does not match response!"
    print(f"  • Supabase row verified: ranking_score={story_db['ranking_score']}, status={story_db['status']}")

    # Check agent_runs
    latest_run = supabase.table("agent_runs") \
        .select("*") \
        .eq("agent_name", "ShortNewsAgent") \
        .order("started_at", desc=True) \
        .limit(1) \
        .execute().data[0]
    print(f"  • agent_runs audit logged: status={latest_run['status']}, duration={latest_run['duration_ms']}ms")
    assert latest_run["status"] == "SUCCESS", "Latest agent run was not SUCCESS"

    print("\n" + "=" * 65)
    print("ALL MILESTONE 4 LIVE INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_live_short_news_and_ranking_test()
