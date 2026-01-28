"""
Relationship data models
"""

from typing import Optional, List

from pydantic import BaseModel


class RelationshipBase(BaseModel):
    """Base relationship model"""

    type: str  # family, friend, enemy, lover, colleague, other
    subtype: Optional[str] = None  # More specific type (e.g., "father", "sister")
    strength: float = 0.5  # Relationship strength 0-1
    description: Optional[str] = None


class RelationshipCreate(RelationshipBase):
    """Relationship creation model"""

    source_id: str
    target_id: str
    first_chapter: int = 1


class Relationship(RelationshipBase):
    """Full relationship model"""

    id: str
    source_id: str
    target_id: str
    source_name: str
    target_name: str
    first_chapter: int = 1
    events: List[str] = []  # Related events

    class Config:
        from_attributes = True


class RelationshipResponse(BaseModel):
    """Relationship API response model"""

    id: str
    source_id: str
    target_id: str
    source_name: str
    target_name: str
    type: str
    subtype: Optional[str]
    strength: float
    first_chapter: int
    description: Optional[str]
