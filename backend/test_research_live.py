import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from main import app
from database import get_supabase_client


def run_live_research_pipeline_test():
    print("=" * 65)
    print("TECHPULSE AI: MILESTONE 3 LIVE INTEGRATION TEST")
    print("=" * 65)

    client = TestClient(app)

    print("\n[1/4] Triggering POST /api/research/run?limit=10&min_relevance=0.50...")
    response = client.post("/api/research/run?limit=10&min_relevance=0.50")

    print(f"HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response Error: {response.text}")
        sys.exit(1)

    data = response.json()
    print("\n[2/4] Validating Response Payload Metrics:")
    print(f"  • Candidate stories evaluated: {data.get('candidate_stories_processed')}")
    print(f"  • Canonical stories created:   {data.get('canonical_stories_created')}")
    print(f"  • Claims extracted:            {data.get('claims_extracted')}")
    print(f"  • Claims confirmed:            {data.get('claims_confirmed')}")
    print(f"  • Claims disputed:             {data.get('claims_disputed')}")
    print(f"  • Claims unconfirmed:          {data.get('claims_unconfirmed')}")
    print(f"  • Average confidence:          {data.get('average_confidence')}%")
    print(f"  • Failed stories count:        {len(data.get('failed_stories', []))}")

    assert data.get("canonical_stories_created", 0) > 0, "No canonical stories created!"
    assert data.get("claims_extracted", 0) > 0, "No claims extracted!"
    assert data.get("average_confidence", 0) > 0, "Average confidence is 0!"

    sample_story = data["results"][0]
    print(f"\nSample Canonical Story Created:")
    print(f"  • Story ID:     {sample_story.get('story_id')}")
    print(f"  • Title:        {sample_story.get('title')}")
    print(f"  • Category:     {sample_story.get('category')}")
    print(f"  • Confidence:   {sample_story.get('confidence')}%")
    print(f"  • Claims Count: {sample_story.get('claims_count')}")
    print(f"  • Sources Tied: {sample_story.get('sources_linked')}")

    print("\n[3/4] Verifying Supabase Database Records:")
    supabase = get_supabase_client()

    # Verify stories table
    story_id = sample_story["story_id"]
    story_row = supabase.table("stories").select("*").eq("id", story_id).execute()
    assert len(story_row.data) > 0, f"Story {story_id} not found in Supabase!"
    s = story_row.data[0]
    print(f"  • Verified in `stories`: title='{s['title'][:50]}...', confidence={s['confidence']}")
    assert s.get("what"), "Story missing 'what'"
    assert s.get("why_it_matters"), "Story missing 'why_it_matters'"
    assert s.get("impact"), "Story missing 'impact'"
    assert 0 <= s.get("confidence", 0) <= 100, "Confidence out of bounds"

    # Verify story_sources table
    sources_linked = supabase.table("story_sources").select("*").eq("story_id", story_id).execute()
    print(f"  • Verified in `story_sources`: {len(sources_linked.data)} source(s) linked.")
    assert len(sources_linked.data) > 0, "No story_sources linked!"

    # Verify claims table
    claims_rows = supabase.table("claims").select("*").eq("story_id", story_id).execute()
    print(f"  • Verified in `claims`: {len(claims_rows.data)} claim(s) stored.")
    assert len(claims_rows.data) > 0, "No claims stored!"
    c_sample = claims_rows.data[0]
    print(f"    - Sample Claim: '{c_sample['claim_text'][:60]}...' | Status: {c_sample['status']}")

    # Verify agent_runs table
    print("\n[4/4] Verifying Agent Telemetry in `agent_runs`:")
    runs = supabase.table("agent_runs") \
        .select("*") \
        .eq("agent_name", "ResearchVerificationAgent") \
        .order("started_at", desc=True) \
        .limit(1) \
        .execute()

    assert len(runs.data) > 0, "No agent_runs record found for ResearchVerificationAgent!"
    latest_run = runs.data[0]
    print(f"  • Run Status:   {latest_run.get('status')}")
    print(f"  • Duration:     {latest_run.get('duration_ms')}ms")
    print(f"  • Output Stats: {latest_run.get('output_payload')}")
    assert latest_run.get("status") == "SUCCESS", "Latest agent run was not SUCCESS!"

    print("\n" + "=" * 65)
    print("ALL MILESTONE 3 LIVE INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_live_research_pipeline_test()
