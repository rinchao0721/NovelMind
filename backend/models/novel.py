"""
Novel data models
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NovelBase(BaseModel):
    """Base novel model"""

    title: str
    author: Optional[str] = None


class NovelCreate(NovelBase):
    """Novel creation model"""

    pass


class Novel(NovelBase):
    """Full novel model"""

    id: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    analysis_status: str = "pending"
    total_chapters: int = 0
    total_words: int = 0

    class Config:
        from_attributes = True


class NovelResponse(BaseModel):
    """Novel API response model"""

    id: str
    title: str
    author: Optional[str] = None
    file_path: Optional[str] = None
    created_at: str
    updated_at: str
    analysis_status: str
    total_chapters: int
    total_words: int

    @classmethod
    def from_orm(cls, novel: Novel) -> "NovelResponse":
        return cls(
            id=novel.id,
            title=novel.title,
            author=novel.author,
            file_path=novel.file_path,
            created_at=novel.created_at.isoformat()
            if isinstance(novel.created_at, datetime)
            else novel.created_at,
            updated_at=novel.updated_at.isoformat()
            if isinstance(novel.updated_at, datetime)
            else novel.updated_at,
            analysis_status=novel.analysis_status,
            total_chapters=novel.total_chapters,
            total_words=novel.total_words,
        )
