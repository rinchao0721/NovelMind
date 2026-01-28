"""
Neo4j database operations for character relationships
"""

from typing import List, Dict, Any

try:
    from neo4j import AsyncGraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from config import settings


class Neo4jDB:
    """Neo4j database helper class for character relationship graph"""

    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self._driver = None

    async def connect(self):
        """Establish connection to Neo4j"""
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package is not installed")

        if not self._driver:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

    async def close(self):
        """Close the database connection"""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            await self.connect()
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 as n")
                record = await result.single()
                return record["n"] == 1
        except Exception:
            return False

    async def create_character(self, character: Dict[str, Any]) -> str:
        """Create a character node"""
        await self.connect()

        query = """
        CREATE (c:Character {
            id: $id,
            name: $name,
            novel_id: $novel_id,
            importance: $importance,
            description: $description
        })
        RETURN c.id as id
        """

        async with self._driver.session() as session:
            result = await session.run(query, **character)
            record = await result.single()
            return record["id"]

    async def create_relationship(
        self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None
    ) -> bool:
        """Create a relationship between two characters"""
        await self.connect()

        props = properties or {}
        query = """
        MATCH (a:Character {id: $source_id})
        MATCH (b:Character {id: $target_id})
        CREATE (a)-[r:RELATIONSHIP {
            type: $rel_type,
            strength: $strength,
            description: $description,
            first_chapter: $first_chapter
        }]->(b)
        RETURN r
        """

        async with self._driver.session() as session:
            result = await session.run(
                query,
                source_id=source_id,
                target_id=target_id,
                rel_type=rel_type,
                strength=props.get("strength", 0.5),
                description=props.get("description", ""),
                first_chapter=props.get("first_chapter", 1),
            )
            return await result.single() is not None

    async def get_graph_data(self, novel_id: str) -> Dict[str, List]:
        """Get all nodes and relationships for a novel"""
        await self.connect()

        query = """
        MATCH (c:Character {novel_id: $novel_id})
        OPTIONAL MATCH (c)-[r:RELATIONSHIP]->(c2:Character)
        RETURN c, r, c2
        """

        nodes = []
        links = []
        seen_nodes = set()

        async with self._driver.session() as session:
            result = await session.run(query, novel_id=novel_id)

            async for record in result:
                char = record["c"]
                if char["id"] not in seen_nodes:
                    nodes.append(
                        {
                            "id": char["id"],
                            "name": char["name"],
                            "importance": char.get("importance", 0.5),
                        }
                    )
                    seen_nodes.add(char["id"])

                rel = record["r"]
                target = record["c2"]
                if rel and target:
                    if target["id"] not in seen_nodes:
                        nodes.append(
                            {
                                "id": target["id"],
                                "name": target["name"],
                                "importance": target.get("importance", 0.5),
                            }
                        )
                        seen_nodes.add(target["id"])

                    links.append(
                        {
                            "source": char["id"],
                            "target": target["id"],
                            "type": rel.get("type", "other"),
                            "strength": rel.get("strength", 0.5),
                        }
                    )

        return {"nodes": nodes, "links": links}

    async def delete_novel_data(self, novel_id: str):
        """Delete all character data for a novel"""
        await self.connect()

        query = """
        MATCH (c:Character {novel_id: $novel_id})
        DETACH DELETE c
        """

        async with self._driver.session() as session:
            await session.run(query, novel_id=novel_id)

    async def get_character_relationships(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a character"""
        await self.connect()

        query = """
        MATCH (c:Character {id: $character_id})-[r:RELATIONSHIP]-(c2:Character)
        RETURN c2.id as target_id, c2.name as target_name, 
               r.type as type, r.strength as strength, r.description as description
        """

        relationships = []
        async with self._driver.session() as session:
            result = await session.run(query, character_id=character_id)

            async for record in result:
                relationships.append(
                    {
                        "target_id": record["target_id"],
                        "target_name": record["target_name"],
                        "type": record["type"],
                        "strength": record["strength"],
                        "description": record["description"],
                    }
                )

        return relationships
