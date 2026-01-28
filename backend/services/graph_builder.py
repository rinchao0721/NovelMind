"""
Graph builder service for Neo4j relationship graphs
"""

from typing import Dict, Any, List

from database.neo4j_db import Neo4jDB
from database.sqlite_db import get_db


class GraphBuilder:
    """Build and manage character relationship graphs"""

    def __init__(self):
        self.neo4j = Neo4jDB()

    async def build_graph(self, novel_id: str) -> Dict[str, Any]:
        """Build a complete graph from SQLite characters and relationships"""

        # Get characters from SQLite
        characters = await self._get_characters(novel_id)

        # Create nodes in Neo4j
        for char in characters:
            try:
                await self.neo4j.create_character(
                    {
                        "id": char["id"],
                        "name": char["name"],
                        "novel_id": novel_id,
                        "importance": char["importance_score"],
                        "description": char.get("description", ""),
                    }
                )
            except Exception as e:
                print(f"Failed to create character node: {e}")

        return await self.get_graph_data(novel_id)

    async def _get_characters(self, novel_id: str) -> List[Dict]:
        """Get characters from SQLite"""
        async with get_db() as db:
            cursor = await db.execute(
                """
                SELECT id, name, aliases, description, personality, 
                       first_appearance, importance_score
                FROM characters WHERE novel_id = ?
                """,
                (novel_id,),
            )
            rows = await cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "aliases": row[2].split(",") if row[2] else [],
                    "description": row[3],
                    "personality": row[4],
                    "first_appearance": row[5],
                    "importance_score": row[6],
                }
                for row in rows
            ]

    async def get_graph_data(self, novel_id: str) -> Dict[str, List]:
        """Get graph data for visualization"""
        try:
            return await self.neo4j.get_graph_data(novel_id)
        except Exception:
            # Fallback to SQLite-only data
            characters = await self._get_characters(novel_id)
            return {
                "nodes": [
                    {"id": c["id"], "name": c["name"], "importance": c["importance_score"]}
                    for c in characters
                ],
                "links": [],
            }

    async def add_relationship(
        self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None
    ) -> bool:
        """Add a relationship to the graph"""
        try:
            return await self.neo4j.create_relationship(source_id, target_id, rel_type, properties)
        except Exception as e:
            print(f"Failed to add relationship: {e}")
            return False

    async def delete_novel_graph(self, novel_id: str):
        """Delete all graph data for a novel"""
        try:
            await self.neo4j.delete_novel_data(novel_id)
        except Exception as e:
            print(f"Failed to delete graph data: {e}")

    async def get_character_network(self, character_id: str, depth: int = 1) -> Dict[str, List]:
        """Get the network around a specific character"""
        try:
            relationships = await self.neo4j.get_character_relationships(character_id)

            nodes = [{"id": character_id, "name": "Current"}]
            links = []

            for rel in relationships:
                nodes.append({"id": rel["target_id"], "name": rel["target_name"]})
                links.append(
                    {
                        "source": character_id,
                        "target": rel["target_id"],
                        "type": rel["type"],
                        "strength": rel["strength"],
                    }
                )

            return {"nodes": nodes, "links": links}

        except Exception as e:
            print(f"Failed to get character network: {e}")
            return {"nodes": [], "links": []}
