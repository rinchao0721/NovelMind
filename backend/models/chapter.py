"""
Chapter data models
"""

from typing import Optional

from pydantic import BaseModel


class ChapterBase(BaseModel):
    """Base chapter model"""

    title: Optional[str] = None
    content: str
    word_count: int = 0


class ChapterCreate(ChapterBase):
    """Chapter creation model"""

    novel_id: str
    chapter_num: int


class Chapter(ChapterBase):
    """Full chapter model"""

    id: str
    novel_id: str
    chapter_num: int
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class ChapterResponse(BaseModel):
    """Chapter API response model"""

    id: str
    novel_id: str
    chapter_num: int
    title: Optional[str]
    word_count: int
    summary: Optional[str]
    # Note: content is excluded from response to reduce payload size
