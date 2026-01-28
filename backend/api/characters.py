"""
Character API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database.sqlite_db import get_db

router = APIRouter()


class CharacterResponse(BaseModel):
    """Character response model"""

    id: str
    novel_id: str
    name: str
    aliases: List[str]
    description: Optional[str]
    personality: Optional[str]
    first_appearance: int
    importance_score: float


@router.get("", response_model=List[CharacterResponse])
async def get_characters(
    novel_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Get list of characters"""
    async with get_db() as db:
        if novel_id:
            cursor = await db.execute(
                """
                SELECT id, novel_id, name, aliases, description, personality, 
                       first_appearance, importance_score
                FROM characters
                WHERE novel_id = ?
                ORDER BY importance_score DESC
                LIMIT ? OFFSET ?
                """,
                (novel_id, limit, skip),
            )
        else:
            cursor = await db.execute(
                """
                SELECT id, novel_id, name, aliases, description, personality,
                       first_appearance, importance_score
                FROM characters
                ORDER BY importance_score DESC
                LIMIT ? OFFSET ?
                """,
                (limit, skip),
            )

        rows = await cursor.fetchall()

        characters = []
        for row in rows:
            aliases = row[3].split(",") if row[3] else []
            characters.append(
                CharacterResponse(
                    id=row[0],
                    novel_id=row[1],
                    name=row[2],
                    aliases=aliases,
                    description=row[4],
                    personality=row[5],
                    first_appearance=row[6] or 1,
                    importance_score=row[7] or 0.5,
                )
            )

        return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """Get a specific character"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, novel_id, name, aliases, description, personality,
                   first_appearance, importance_score
            FROM characters WHERE id = ?
            """,
            (character_id,),
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Character not found")

        aliases = row[3].split(",") if row[3] else []
        return CharacterResponse(
            id=row[0],
            novel_id=row[1],
            name=row[2],
            aliases=aliases,
            description=row[4],
            personality=row[5],
            first_appearance=row[6] or 1,
            importance_score=row[7] or 0.5,
        )
