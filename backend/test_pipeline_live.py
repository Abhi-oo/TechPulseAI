import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from main import app
from database import get_supabase_client


def test_live_discovery_endpoint():
    print("=" * 60)
    print("TECHPULSE AI: MILESTONE 2 LIVE INTEGRATION TEST")
    print("=" * 60)

    client = TestClient(app)

    print("\n[1/4] Triggering POST /api/discovery/run...")
    response = client.post("/api/discovery/run")

    print(f"HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response Error: {response.text}")
        sys.exit(1)

    data = response.json()
    print("\n[2/4] Validating Endpoint Response Schema:")
    print(f"  • articles_scanned: {data.get('articles_scanned')}")
    print(f"  • new_articles:     {data.get('new_articles')}")
    print(f"  • candidate_stories:{len(data.get('candidate_stories', []))}")
    print(f"  • failed feeds:     {data.get('failed')}")

    assert "articles_scanned" in data, "Missing articles_scanned"
    assert "new_articles" in data, "Missing new_articles"
    assert "candidate_stories" in data, "Missing candidate_stories"
    assert "failed" in data, "Missing failed"

    if data.get("candidate_stories"):
        sample = data["candidate_stories"][0]
        print(f"\nSample Candidate Story:")
        print(f"  • Title:     {sample.get('title')}")
        print(f"  • Category:  {sample.get('category')}")
        print(f"  • Score:     {sample.get('relevance_score')}")
        print(f"  • Keywords:  {sample.get('matched_keywords')}")

    print("\n[3/4] Verifying Supabase Database State:")
    supabase = get_supabase_client()

    # Check sources
    src_res = supabase.table("sources").select("count", count="exact").execute()
    print(f"  • sources count in DB:     {src_res.count}")
    assert src_res.count > 0, "No sources found in DB!"

    # Check submissions
    sub_res = supabase.table("submissions").select("count", count="exact").execute()
    print(f"  • submissions count in DB: {sub_res.count}")
    assert sub_res.count > 0, "No submissions found in DB!"

    # Check agent_runs
    runs_res = supabase.table("agent_runs") \
        .select("*") \
        .eq("agent_name", "DiscoveryAgent") \
        .order("started_at", desc=True) \
        .limit(1) \
        .execute()

    print(f"  • agent_runs count:        {len(runs_res.data)}")
    assert len(runs_res.data) > 0, "No agent_runs recorded!"
    latest_run = runs_res.data[0]
    print(f"  • Latest Run Status:       {latest_run.get('status')}")
    print(f"  • Latest Run Duration:     {latest_run.get('duration_ms')}ms")
    print(f"  • Latest Run Output:       {latest_run.get('output_payload')}")
    assert latest_run.get("status") == "SUCCESS", "Latest run status is not SUCCESS!"

    print("\n[4/4] Deduplication Verification:")
    print("Triggering second run to verify deduplication...")
    second_response = client.post("/api/discovery/run")
    second_data = second_response.json()
    print(f"  • First run new articles:  {data.get('new_articles')}")
    print(f"  • Second run new articles: {second_data.get('new_articles')} (Expected 0 or near 0)")
    assert second_data.get("new_articles") == 0 or second_data.get("new_articles") < data.get("new_articles"), "Deduplication failed!"

    print("\n" + "=" * 60)
    print("ALL MILESTONE 2 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_live_discovery_endpoint()
