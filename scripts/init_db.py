"""Initialize the ARRS database."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arrs.storage.database import Database
from config import settings


async def main():
    """Initialize database with schema."""
    # Extract path from URL (remove sqlite:///)
    db_path = settings.database_url.replace("sqlite:///", "")

    print(f"Initializing database at: {db_path}")

    db = Database(db_path)
    await db.initialize()

    print("✓ Database initialized successfully!")
    print(f"✓ Schema created")
    print(f"✓ Indexes created")


if __name__ == "__main__":
    asyncio.run(main())
