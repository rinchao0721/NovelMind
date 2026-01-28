import networkx as nx
from typing import List, Dict, Optional
from database.sqlite_db import get_db
from utils.logger import logger


class GraphService:
    """Service for graph operations using NetworkX"""

    async def build_graph(self, novel_id: str) -> nx.Graph:
        """Build NetworkX graph from SQLite data"""
        G = nx.Graph()

        try:
            async with get_db() as db:
                # Load characters as nodes
                cursor = await db.execute(
                    "SELECT id, name, importance_score FROM characters WHERE novel_id = ?",
                    (novel_id,),
                )
                characters = await cursor.fetchall()
                for char in characters:
                    G.add_node(char[0], name=char[1], importance=char[2] or 0.5)

                # Load relationships as edges
                cursor = await db.execute(
                    "SELECT source_id, target_id, type, strength FROM relationships WHERE novel_id = ?",
                    (novel_id,),
                )
                relationships = await cursor.fetchall()
                for rel in relationships:
                    # NetworkX handles duplicate edges by updating attributes if we use add_edge
                    # But for multigraph behavior we might need MultiGraph.
                    # For simple visualization, simple Graph is usually enough, taking the strongest link or merging.
                    # Here we just add edge.
                    if G.has_edge(rel[0], rel[1]):
                        # If edge exists, maybe update weight or type?
                        # For now, let's keep it simple.
                        pass
                    else:
                        G.add_edge(rel[0], rel[1], type=rel[2], weight=rel[3] or 0.5)

            return G
        except Exception as e:
            logger.error(f"Error building graph from DB: {e}", exc_info=True)
            return nx.Graph()

    async def get_graph_data(self, novel_id: str) -> Dict[str, List]:
        """Get graph data formatted for frontend (ECharts)"""
        try:
            G = await self.build_graph(novel_id)

            if G.number_of_nodes() == 0:
                return {"nodes": [], "links": []}

            # Optional: Calculate communities for coloring
            try:
                communities = nx.community.louvain_communities(G)
                # Map node_id to community index
                community_map = {}
                for idx, comm in enumerate(communities):
                    for node_id in comm:
                        community_map[node_id] = idx
            except Exception:
                # Fallback if community detection fails or library missing
                community_map = {}

            nodes = []
            for node_id, data in G.nodes(data=True):
                nodes.append(
                    {
                        "id": node_id,
                        "name": data.get("name", "Unknown"),
                        "importance": data.get("importance", 0.5),
                        "category": community_map.get(node_id, 0),
                    }
                )

            links = []
            for u, v, data in G.edges(data=True):
                links.append(
                    {
                        "source": u,
                        "target": v,
                        "type": data.get("type", "other"),
                        "value": data.get("weight", 0.5),
                    }
                )

            logger.info(
                f"Generated graph data for {novel_id}: {len(nodes)} nodes, {len(links)} links"
            )
            return {"nodes": nodes, "links": links}

        except Exception as e:
            logger.error(f"Error generating graph data for {novel_id}: {e}", exc_info=True)
            return {"nodes": [], "links": []}

    async def get_centrality(self, novel_id: str) -> Dict[str, float]:
        """Calculate centrality measures"""
        G = await self.build_graph(novel_id)
        if G.number_of_nodes() == 0:
            return {}
        return nx.degree_centrality(G)


# Singleton instance
_graph_service: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
