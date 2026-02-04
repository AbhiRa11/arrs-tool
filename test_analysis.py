"""Quick test script to debug analysis errors."""
import asyncio
from arrs.storage.database import Database
from arrs.storage.json_store import JSONStore
from arrs.storage.repository import Repository
from arrs.core.orchestrator import AnalysisOrchestrator
from config import settings

async def test_analysis():
    """Test a simple analysis."""
    # Setup
    db_path = settings.database_url.replace("sqlite:///", "")
    db = Database(db_path)
    json_store = JSONStore(settings.json_storage_path)
    repository = Repository(db, json_store)

    orchestrator = AnalysisOrchestrator(repository)

    # Run analysis
    print("Starting analysis...")
    try:
        analysis_id = await orchestrator.analyze_url(
            url="https://example.com",
            brand="Example",
            product_category="website",
            use_case="testing"
        )
        print(f"Success! Analysis ID: {analysis_id}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analysis())
