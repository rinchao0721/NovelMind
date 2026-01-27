"""
Export Service - Export analysis results in various formats
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from database.sqlite_db import get_db


class ExportService:
    """Service for exporting analysis results"""

    async def get_novel_data(self, novel_id: str) -> Dict[str, Any]:
        """Get all data for a novel including characters and relationships"""
        async with get_db() as db:
            # Get novel info
            cursor = await db.execute("SELECT * FROM novels WHERE id = ?", (novel_id,))
            novel_row = await cursor.fetchone()

            if not novel_row:
                raise ValueError(f"Novel not found: {novel_id}")

            novel = {
                "id": novel_row[0],
                "title": novel_row[1],
                "author": novel_row[2],
                "file_path": novel_row[3],
                "word_count": novel_row[4],
                "created_at": novel_row[5],
            }

            # Get chapters
            cursor = await db.execute(
                "SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_number",
                (novel_id,),
            )
            chapters_rows = await cursor.fetchall()
            chapters = []
            for row in chapters_rows:
                chapters.append(
                    {
                        "id": row[0],
                        "chapter_number": row[2],
                        "title": row[3],
                        "summary": row[5] if len(row) > 5 else None,
                    }
                )

            # Get characters
            cursor = await db.execute("SELECT * FROM characters WHERE novel_id = ?", (novel_id,))
            characters_rows = await cursor.fetchall()
            characters = []
            for row in characters_rows:
                characters.append(
                    {
                        "id": row[0],
                        "name": row[2],
                        "aliases": json.loads(row[3]) if row[3] else [],
                        "description": row[4],
                        "personality": row[5] if len(row) > 5 else None,
                        "importance": row[6] if len(row) > 6 else 0.5,
                    }
                )

            # Get relationships
            cursor = await db.execute("SELECT * FROM relationships WHERE novel_id = ?", (novel_id,))
            relationships_rows = await cursor.fetchall()
            relationships = []
            for row in relationships_rows:
                relationships.append(
                    {
                        "id": row[0],
                        "source_id": row[2],
                        "target_id": row[3],
                        "type": row[4],
                        "subtype": row[5] if len(row) > 5 else None,
                        "description": row[6] if len(row) > 6 else None,
                        "strength": row[7] if len(row) > 7 else 0.5,
                    }
                )

            # Get plot events
            cursor = await db.execute(
                "SELECT * FROM plot_events WHERE novel_id = ? ORDER BY event_order",
                (novel_id,),
            )
            events_rows = await cursor.fetchall()
            events = []
            for row in events_rows:
                events.append(
                    {
                        "id": row[0],
                        "title": row[2],
                        "description": row[3],
                        "chapter_id": row[4] if len(row) > 4 else None,
                        "event_type": row[5] if len(row) > 5 else None,
                        "importance": row[6] if len(row) > 6 else 0.5,
                    }
                )

            return {
                "novel": novel,
                "chapters": chapters,
                "characters": characters,
                "relationships": relationships,
                "events": events,
                "exported_at": datetime.now().isoformat(),
            }

    async def export_json(self, novel_id: str) -> str:
        """Export analysis results as JSON string"""
        data = await self.get_novel_data(novel_id)
        return json.dumps(data, ensure_ascii=False, indent=2)

    async def export_markdown(self, novel_id: str) -> str:
        """Export analysis results as Markdown"""
        data = await self.get_novel_data(novel_id)
        novel = data["novel"]
        characters = data["characters"]
        relationships = data["relationships"]
        events = data.get("events", [])

        lines = []

        # Title
        lines.append(f"# {novel['title']}")
        if novel.get("author"):
            lines.append(f"\n**作者**: {novel['author']}")
        lines.append(f"\n**字数**: {novel.get('word_count', 'N/A')}")
        lines.append(f"\n**导出时间**: {data['exported_at']}")
        lines.append("\n---\n")

        # Characters
        lines.append("## 人物列表\n")
        if characters:
            # Sort by importance
            sorted_chars = sorted(characters, key=lambda x: x.get("importance", 0), reverse=True)
            for char in sorted_chars:
                importance_stars = "★" * int(char.get("importance", 0.5) * 5)
                lines.append(f"### {char['name']} {importance_stars}\n")
                if char.get("aliases"):
                    lines.append(f"**别名**: {', '.join(char['aliases'])}\n")
                if char.get("description"):
                    lines.append(f"{char['description']}\n")
                if char.get("personality"):
                    lines.append(f"\n**性格特点**: {char['personality']}\n")
                lines.append("")
        else:
            lines.append("*暂无人物数据*\n")

        lines.append("\n---\n")

        # Relationships
        lines.append("## 人物关系\n")
        if relationships:
            # Group by relationship type
            rel_by_type: Dict[str, List[Dict[str, Any]]] = {}
            for rel in relationships:
                rel_type = rel.get("type", "other")
                if rel_type not in rel_by_type:
                    rel_by_type[rel_type] = []
                rel_by_type[rel_type].append(rel)

            type_names = {
                "family": "家庭关系",
                "friend": "朋友关系",
                "enemy": "敌对关系",
                "lover": "恋人关系",
                "colleague": "同事关系",
                "other": "其他关系",
            }

            # Create character id to name mapping
            char_map = {c["id"]: c["name"] for c in characters}

            for rel_type, rels in rel_by_type.items():
                lines.append(f"### {type_names.get(rel_type, rel_type)}\n")
                for rel in rels:
                    source_name = char_map.get(rel["source_id"], rel["source_id"])
                    target_name = char_map.get(rel["target_id"], rel["target_id"])
                    subtype = f" ({rel['subtype']})" if rel.get("subtype") else ""
                    lines.append(f"- **{source_name}** ↔ **{target_name}**{subtype}")
                    if rel.get("description"):
                        lines.append(f"  - {rel['description']}")
                lines.append("")
        else:
            lines.append("*暂无关系数据*\n")

        lines.append("\n---\n")

        # Plot Events
        if events:
            lines.append("## 关键事件\n")
            for i, event in enumerate(events, 1):
                importance_indicator = (
                    "🔴"
                    if event.get("importance", 0) > 0.7
                    else "🟡"
                    if event.get("importance", 0) > 0.4
                    else "🟢"
                )
                lines.append(f"### {i}. {event['title']} {importance_indicator}\n")
                if event.get("event_type"):
                    type_names = {
                        "conflict": "冲突",
                        "revelation": "揭示",
                        "turning_point": "转折点",
                        "climax": "高潮",
                        "resolution": "解决",
                    }
                    lines.append(
                        f"**类型**: {type_names.get(event['event_type'], event['event_type'])}\n"
                    )
                if event.get("description"):
                    lines.append(f"{event['description']}\n")
                lines.append("")

        # Footer
        lines.append("\n---\n")
        lines.append("*由 NovelMind 生成*")

        return "\n".join(lines)


# Singleton
_export_service: Optional[ExportService] = None


def get_export_service() -> ExportService:
    """Get export service singleton"""
    global _export_service
    if _export_service is None:
        _export_service = ExportService()
    return _export_service
