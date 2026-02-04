"""Test script to verify ARRS setup."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from arrs.storage.database import Database
        from arrs.storage.json_store import JSONStore
        from arrs.storage.repository import Repository
        from arrs.crawlers.beautifulsoup_crawler import BeautifulSoupCrawler
        from arrs.parsers.html_parser import HTMLParser
        from arrs.parsers.schema_parser import SchemaParser
        from arrs.engines.ade.engine import ADEEngine
        from arrs.engines.arce.engine import ARCEEngine
        from arrs.engines.tre.engine import TREEngine
        from arrs.simulation.simulator import ClaudeSimulator
        from arrs.core.orchestrator import AnalysisOrchestrator
        from arrs.reporting.report_generator import ReportGenerator
        from config import settings

        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


async def test_config():
    """Test configuration."""
    print("\nTesting configuration...")

    try:
        from config import settings

        print(f"  Database URL: {settings.database_url}")
        print(f"  JSON storage: {settings.json_storage_path}")
        print(f"  ADE weight: {settings.weight_ade}")
        print(f"  ARCE weight: {settings.weight_arce}")
        print(f"  TRE weight: {settings.weight_tre}")

        # Check API key
        if settings.anthropic_api_key and settings.anthropic_api_key != "sk-ant-your-key-here":
            print("  ✓ Anthropic API key configured")
        else:
            print("  ⚠ Anthropic API key not configured (simulation will fail)")

        print("✓ Configuration loaded")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


async def test_database():
    """Test database initialization."""
    print("\nTesting database...")

    try:
        from arrs.storage.database import Database
        from config import settings

        db_path = settings.database_url.replace("sqlite:///", "")
        db = Database(db_path)

        # Initialize schema
        await db.initialize()
        print("✓ Database initialized")

        # Test connection
        conn = await db.get_connection()
        await conn.close()
        print("✓ Database connection successful")

        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


async def test_crawler():
    """Test basic crawler functionality."""
    print("\nTesting crawler...")

    try:
        from arrs.crawlers.beautifulsoup_crawler import BeautifulSoupCrawler

        crawler = BeautifulSoupCrawler()

        # Test with a simple site
        content = await crawler.crawl("https://example.com", "test-analysis")

        print(f"✓ Crawler successful")
        print(f"  URL: {content.url}")
        print(f"  Status: {content.status_code}")
        print(f"  Content length: {len(content.html_content)} chars")

        return True
    except Exception as e:
        print(f"✗ Crawler test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ARRS System Setup Test")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_imports())
    results.append(await test_config())
    results.append(await test_database())
    results.append(await test_crawler())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("\nSystem is ready to use!")
        print("\nNext steps:")
        print("  1. Add your Anthropic API key to .env")
        print("  2. Run: python cli.py analyze <url>")
    else:
        print(f"⚠ {passed}/{total} tests passed")
        print("\nPlease fix the failures above before using the system.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
