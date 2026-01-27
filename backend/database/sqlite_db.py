"""
SQLite database operations
"""
import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path

from config import settings


# Database schema
SCHEMA = """
-- 小说表
CREATE TABLE IF NOT EXISTS novels (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    file_path TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    analysis_status TEXT DEFAULT 'pending',
    total_chapters INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0
);

-- 章节表
CREATE TABLE IF NOT EXISTS chapters (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    chapter_num INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    summary TEXT,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 人物表
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    name TEXT NOT NULL,
    aliases TEXT,
    description TEXT,
    personality TEXT,
    first_appearance INTEGER,
    importance_score REAL DEFAULT 0.5,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 设置表
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chapters_novel_id ON chapters(novel_id);
CREATE INDEX IF NOT EXISTS idx_characters_novel_id ON characters(novel_id);
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_novel_id ON analysis_tasks(novel_id);
"""


async def init_db():
    """Initialize the database with schema"""
    db_path = settings.DATABASE_PATH
    
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(db_path) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        await db.executescript(SCHEMA)
        await db.commit()


@asynccontextmanager
async def get_db():
    """Get database connection context manager"""
    db = await aiosqlite.connect(settings.DATABASE_PATH)
    try:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        yield db
    finally:
        await db.close()


class SQLiteDB:
    """SQLite database helper class"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DATABASE_PATH
    
    async def execute(self, query: str, params: tuple = None):
        """Execute a query"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            await db.commit()
            return cursor
    
    async def fetch_one(self, query: str, params: tuple = None):
        """Fetch a single row"""
        async with aiosqlite.connect(self.db_path) as db:
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = None):
        """Fetch all rows"""
        async with aiosqlite.connect(self.db_path) as db:
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            return await cursor.fetchall()
