"""
Character data models
"""
from typing import Optional, List

from pydantic import BaseModel


class CharacterBase(BaseModel):
    """Base character model"""
    name: str
    aliases: List[str] = []
    description: Optional[str] = None
    personality: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Character creation model"""
    novel_id: str
    first_appearance: int = 1
    importance_score: float = 0.5


class Character(CharacterBase):
    """Full character model"""
    id: str
    novel_id: str
    first_appearance: int = 1
    importance_score: float = 0.5
    
    class Config:
        from_attributes = True


class CharacterResponse(BaseModel):
    """Character API response model"""
    id: str
    novel_id: str
    name: str
    aliases: List[str]
    description: Optional[str]
    personality: Optional[str]
    first_appearance: int
    importance_score: float
