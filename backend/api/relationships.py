"""
Relationships API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database.sqlite_db import get_db
from services.graph_service import get_graph_service

router = APIRouter()


class RelationshipResponse(BaseModel):
    """Relationship response model"""

    id: str
    source_id: str
    target_id: str
    source_name: str
    target_name: str
    type: str
    strength: float
    description: Optional[str]


class GraphDataResponse(BaseModel):
    """Graph data response model"""

    nodes: List[dict]
    links: List[dict]


@router.get("/{novel_id}", response_model=List[RelationshipResponse])
async def get_relationships(novel_id: str):
    """Get all relationships for a novel"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT r.id, r.source_id, r.target_id, 
                   c1.name as source_name, c2.name as target_name,
                   r.type, r.strength, r.description
            FROM relationships r
            JOIN characters c1 ON r.source_id = c1.id
            JOIN characters c2 ON r.target_id = c2.id
            WHERE r.novel_id = ?
            """,
            (novel_id,),
        )
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "source_id": row[1],
                "target_id": row[2],
                "source_name": row[3],
                "target_name": row[4],
                "type": row[5],
                "strength": row[6],
                "description": row[7],
            }
            for row in rows
        ]


@router.get("/{novel_id}/graph", response_model=GraphDataResponse)
async def get_graph_data(novel_id: str):
    """Get relationship graph data for visualization"""
    graph_service = get_graph_service()
    return await graph_service.get_graph_data(novel_id)
