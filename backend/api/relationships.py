"""
Relationships API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database.sqlite_db import get_db

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
    """Get all relationships for a novel (from Neo4j in production)"""
    # This would query Neo4j in production
    # For now, return empty list
    return []


@router.get("/{novel_id}/graph", response_model=GraphDataResponse)
async def get_graph_data(novel_id: str):
    """Get relationship graph data for visualization"""
    async with get_db() as db:
        # Get characters as nodes
        cursor = await db.execute(
            """
            SELECT id, name, importance_score
            FROM characters
            WHERE novel_id = ?
            """,
            (novel_id,),
        )
        rows = await cursor.fetchall()

        nodes = [
            {
                "id": row[0],
                "name": row[1],
                "importance": row[2] or 0.5,
                "category": 0,  # Would be determined by character type
            }
            for row in rows
        ]

        # In production, links would come from Neo4j
        links = []

        return GraphDataResponse(nodes=nodes, links=links)
