"""
Analysis Engine - Core analysis logic for novel processing
"""

import uuid
from typing import Dict, Any, List

from database.sqlite_db import get_db
from database.neo4j_db import Neo4jDB
from services.llm_service import LLMService


class AnalysisEngine:
    """Main analysis engine for novel processing"""

    def __init__(self):
        self.llm = LLMService()
        self.neo4j = Neo4jDB()

    async def analyze(self, novel_id: str, task_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run full analysis on a novel"""

        features = config.get("features", ["characters", "relationships", "plot", "summary"])
        depth = config.get("depth", "standard")

        # Get novel chapters
        chapters = await self._get_chapters(novel_id, config)

        if not chapters:
            raise ValueError("No chapters found for analysis")

        # Initialize result
        result = {
            "novel_id": novel_id,
            "task_id": task_id,
            "characters": [],
            "relationships": [],
            "plots": [],
            "chapter_summaries": [],
        }

        # Update progress
        total_steps = len(
            [f for f in features if f in ["characters", "relationships", "plot", "summary"]]
        )
        current_step = 0

        # Step 1: Character extraction
        if "characters" in features:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "识别人物...")
            result["characters"] = await self._extract_characters(novel_id, chapters, depth)
            current_step += 1

        # Step 2: Relationship analysis
        if "relationships" in features and result["characters"]:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "分析关系...")
            result["relationships"] = await self._analyze_relationships(
                novel_id, result["characters"], chapters, depth
            )
            current_step += 1

        # Step 3: Plot tracking
        if "plot" in features:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "追踪情节...")
            result["plots"] = await self._track_plots(novel_id, chapters, depth)
            current_step += 1

        # Step 4: Summary generation
        if "summary" in features:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "生成摘要...")
            result["chapter_summaries"] = await self._generate_summaries(novel_id, chapters, depth)
            current_step += 1

        return result

    async def _get_chapters(self, novel_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get chapters for analysis based on config"""
        async with get_db() as db:
            if config.get("scope") == "partial":
                start = config.get("chapter_start", 1)
                end = config.get("chapter_end", 100)
                cursor = await db.execute(
                    """
                    SELECT id, chapter_num, title, content, word_count
                    FROM chapters
                    WHERE novel_id = ? AND chapter_num >= ? AND chapter_num <= ?
                    ORDER BY chapter_num
                    """,
                    (novel_id, start, end),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT id, chapter_num, title, content, word_count
                    FROM chapters
                    WHERE novel_id = ?
                    ORDER BY chapter_num
                    """,
                    (novel_id,),
                )

            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "chapter_num": row[1],
                    "title": row[2],
                    "content": row[3],
                    "word_count": row[4],
                }
                for row in rows
            ]

    async def _extract_characters(
        self, novel_id: str, chapters: List[Dict], depth: str
    ) -> List[Dict]:
        """Extract characters from novel"""
        all_characters = {}

        # Combine chapter texts for analysis
        # For deeper analysis, analyze more chapters
        sample_size = {"quick": 3, "standard": 10, "deep": len(chapters)}[depth]
        sampled_chapters = chapters[:sample_size]

        combined_text = "\n\n".join(
            [f"【{ch['title']}】\n{ch['content'][:3000]}" for ch in sampled_chapters]
        )

        try:
            characters = await self.llm.analyze_characters(combined_text)

            for char in characters:
                name = char.get("name", "").strip()
                if not name:
                    continue

                if name not in all_characters:
                    char_id = str(uuid.uuid4())
                    all_characters[name] = {
                        "id": char_id,
                        "novel_id": novel_id,
                        "name": name,
                        "aliases": char.get("aliases", []),
                        "description": char.get("description", ""),
                        "personality": char.get("personality", ""),
                        "first_appearance": 1,
                        "importance_score": char.get("importance", 0.5),
                    }

            # Save to database
            async with get_db() as db:
                for char in all_characters.values():
                    await db.execute(
                        """
                        INSERT INTO characters (id, novel_id, name, aliases, description, 
                                               personality, first_appearance, importance_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            char["id"],
                            char["novel_id"],
                            char["name"],
                            ",".join(char["aliases"]),
                            char["description"],
                            char["personality"],
                            char["first_appearance"],
                            char["importance_score"],
                        ),
                    )
                await db.commit()

            return list(all_characters.values())

        except Exception as e:
            print(f"Character extraction error: {e}")
            return []

    async def _analyze_relationships(
        self, novel_id: str, characters: List[Dict], chapters: List[Dict], depth: str
    ) -> List[Dict]:
        """Analyze relationships between characters"""
        sample_size = {"quick": 3, "standard": 10, "deep": len(chapters)}[depth]
        sampled_chapters = chapters[:sample_size]

        combined_text = "\n\n".join(
            [f"【{ch['title']}】\n{ch['content'][:2000]}" for ch in sampled_chapters]
        )

        try:
            relationships = await self.llm.analyze_relationships(characters, combined_text)

            # Create name to ID mapping
            name_to_id = {c["name"]: c["id"] for c in characters}

            result = []
            for rel in relationships:
                source_name = rel.get("source", "")
                target_name = rel.get("target", "")

                source_id = name_to_id.get(source_name)
                target_id = name_to_id.get(target_name)

                if source_id and target_id:
                    rel_data = {
                        "id": str(uuid.uuid4()),
                        "source_id": source_id,
                        "target_id": target_id,
                        "source_name": source_name,
                        "target_name": target_name,
                        "type": rel.get("type", "other"),
                        "subtype": rel.get("subtype"),
                        "strength": rel.get("strength", 0.5),
                        "first_chapter": 1,
                        "description": rel.get("description", ""),
                    }
                    result.append(rel_data)

                    # Save to Neo4j if available
                    try:
                        await self.neo4j.create_relationship(
                            source_id,
                            target_id,
                            rel_data["type"],
                            {
                                "strength": rel_data["strength"],
                                "description": rel_data["description"],
                                "first_chapter": rel_data["first_chapter"],
                            },
                        )
                    except Exception:
                        pass  # Neo4j might not be available

            return result

        except Exception as e:
            print(f"Relationship analysis error: {e}")
            return []

    async def _track_plots(self, novel_id: str, chapters: List[Dict], depth: str) -> List[Dict]:
        """Track plot developments (placeholder)"""
        # This would involve more complex analysis
        # For now, return empty list
        return []

    async def _generate_summaries(
        self, novel_id: str, chapters: List[Dict], depth: str
    ) -> List[Dict]:
        """Generate chapter summaries"""
        summaries = []

        # Limit number of summaries based on depth
        max_chapters = {"quick": 5, "standard": 20, "deep": len(chapters)}[depth]

        for chapter in chapters[:max_chapters]:
            try:
                summary = await self.llm.generate_summary(chapter["content"])

                # Update chapter in database
                async with get_db() as db:
                    await db.execute(
                        "UPDATE chapters SET summary = ? WHERE id = ?", (summary, chapter["id"])
                    )
                    await db.commit()

                summaries.append(
                    {
                        "chapter_id": chapter["id"],
                        "chapter_num": chapter["chapter_num"],
                        "summary": summary,
                    }
                )

            except Exception as e:
                print(f"Summary generation error for chapter {chapter['chapter_num']}: {e}")

        return summaries

    async def _update_progress(self, task_id: str, progress: float, message: str = None):
        """Update task progress in database"""
        async with get_db() as db:
            await db.execute(
                "UPDATE analysis_tasks SET progress = ? WHERE id = ?", (progress, task_id)
            )
            await db.commit()
