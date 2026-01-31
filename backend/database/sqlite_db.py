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

-- 关系表
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT,
    subtype TEXT,
    description TEXT,
    strength REAL DEFAULT 0.5,
    first_chapter INTEGER,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- 情节事件表
CREATE TABLE IF NOT EXISTS plot_events (
    id TEXT PRIMARY KEY,
    novel_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    chapter_id TEXT,
    event_type TEXT,
    importance REAL DEFAULT 0.5,
    event_order INTEGER,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
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
    progress_message TEXT DEFAULT '准备中...',
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chapters_novel_id ON chapters(novel_id);
CREATE INDEX IF NOT EXISTS idx_characters_novel_id ON characters(novel_id);
CREATE INDEX IF NOT EXISTS idx_relationships_novel_id ON relationships(novel_id);
CREATE INDEX IF NOT EXISTS idx_relationships_source_id ON relationships(source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target_id ON relationships(target_id);
CREATE INDEX IF NOT EXISTS idx_plot_events_novel_id ON plot_events(novel_id);
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

        # Check if progress_message column exists (for migration)
        cursor = await db.execute("PRAGMA table_info(analysis_tasks)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'progress_message' not in column_names:
            await db.execute(
                "ALTER TABLE analysis_tasks ADD COLUMN progress_message TEXT DEFAULT '准备中...'"
            )
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
