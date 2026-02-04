"""SQLite database management for ARRS system."""
import aiosqlite
import json
from pathlib import Path
from typing import Optional
from arrs.utils.logger import setup_logger

logger = setup_logger(__name__)

# Database schema
SCHEMA = """
-- analyses: Track each analysis session
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    composite_score REAL,
    metadata TEXT,
    error_message TEXT
);

-- crawled_pages: Store crawled content metadata
CREATE TABLE IF NOT EXISTS crawled_pages (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    url TEXT NOT NULL,
    html_content TEXT,
    crawled_at TIMESTAMP NOT NULL,
    crawl_method TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- engine_scores: Individual engine results
CREATE TABLE IF NOT EXISTS engine_scores (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    engine_name TEXT NOT NULL,
    score REAL NOT NULL,
    weight REAL NOT NULL,
    details TEXT,
    calculated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- simulation_results: Claude API simulation outcomes
CREATE TABLE IF NOT EXISTS simulation_results (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    brand_cited INTEGER NOT NULL,
    citation_count INTEGER NOT NULL,
    missing_signals TEXT,
    simulated_at TIMESTAMP NOT NULL,
    metadata TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- gaps: Actionable improvement recommendations
CREATE TABLE IF NOT EXISTS gaps (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    gap_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    engine_source TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_analyses_url ON analyses(url);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_crawled_pages_analysis_id ON crawled_pages(analysis_id);
CREATE INDEX IF NOT EXISTS idx_engine_scores_analysis_id ON engine_scores(analysis_id);
CREATE INDEX IF NOT EXISTS idx_simulation_results_analysis_id ON simulation_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_gaps_analysis_id ON gaps(analysis_id);
"""


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure the database directory exists."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()
            logger.info("Database initialized successfully", extra={"db_path": self.db_path})

    async def get_connection(self) -> aiosqlite.Connection:
        """
        Get database connection.

        Returns:
            Async database connection
        """
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn

    async def execute(self, query: str, params: Optional[tuple] = None):
        """
        Execute a single query.

        Args:
            query: SQL query
            params: Query parameters
        """
        async with aiosqlite.connect(self.db_path) as db:
            if params:
                await db.execute(query, params)
            else:
                await db.execute(query)
            await db.commit()

    async def executemany(self, query: str, params_list: list):
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query
            params_list: List of parameter tuples
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(query, params_list)
            await db.commit()

    async def fetch_one(self, query: str, params: Optional[tuple] = None):
        """
        Fetch a single row.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Single row or None
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: Optional[tuple] = None):
        """
        Fetch all rows.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List of rows
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchall()


# Utility functions for JSON serialization
def serialize_json_field(data: any) -> str:
    """Serialize data to JSON string for database storage."""
    if data is None:
        return None
    return json.dumps(data)


def deserialize_json_field(data: str) -> any:
    """Deserialize JSON string from database."""
    if data is None:
        return {}
    return json.loads(data)
