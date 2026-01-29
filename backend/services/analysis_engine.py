"""
Analysis Engine - Core analysis logic for novel processing
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional

from database.sqlite_db import get_db


from services.llm_service import LLMService
from utils.logger import logger


class AnalysisEngine:
    """Main analysis engine for novel processing"""

    def __init__(self):
        self.llm = LLMService()

    async def analyze(self, novel_id: str, task_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run full analysis on a novel"""
        logger.info(f"Starting analysis for novel {novel_id} (Task: {task_id})")
        logger.debug(f"Analysis config: {config}")

        features = config.get("features", ["characters", "relationships", "plot", "summary"])
        depth = config.get("depth", "standard")
        provider = config.get("provider")
        model = config.get("model")

        # Get novel chapters
        chapters = await self._get_chapters(novel_id, config)

        if not chapters:
            logger.error(f"No chapters found for novel {novel_id}")
            raise ValueError("No chapters found for analysis")

        logger.info(f"Loaded {len(chapters)} chapters for analysis")

        # Clear existing analysis data to prevent accumulation
        async with get_db() as db:
            await db.execute("DELETE FROM characters WHERE novel_id = ?", (novel_id,))
            await db.execute("DELETE FROM relationships WHERE novel_id = ?", (novel_id,))
            await db.execute("DELETE FROM plot_events WHERE novel_id = ?", (novel_id,))
            await db.execute("UPDATE chapters SET summary = NULL WHERE novel_id = ?", (novel_id,))
            await db.commit()
        logger.info(f"Cleared existing analysis data for novel {novel_id}")

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
            logger.info("Step 1: Extracting characters")
            result["characters"] = await self._extract_characters(
                novel_id, chapters, depth, provider, model
            )
            current_step += 1

        # Step 2: Relationship analysis
        if "relationships" in features and result["characters"]:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "分析关系...")
            logger.info("Step 2: Analyzing relationships")
            result["relationships"] = await self._analyze_relationships(
                novel_id, result["characters"], chapters, depth, provider, model
            )
            current_step += 1

        # Step 3: Plot tracking
        if "plot" in features:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "追踪情节...")
            logger.info("Step 3: Tracking plots")
            result["plots"] = await self._track_plots(novel_id, chapters, depth, provider, model)
            current_step += 1

        # Step 4: Summary generation
        if "summary" in features:
            await self._update_progress(task_id, (current_step / total_steps) * 100, "生成摘要...")
            logger.info("Step 4: Generating summaries")
            result["chapter_summaries"] = await self._generate_summaries(
                novel_id, chapters, depth, provider, model
            )
            current_step += 1

        logger.info(f"Analysis completed for task {task_id}")
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
        self,
        novel_id: str,
        chapters: List[Dict],
        depth: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
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
            characters = await self.llm.analyze_characters(
                combined_text, provider=provider, model=model
            )

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

            logger.info(f"Saved {len(all_characters)} characters to SQLite database")

            return list(all_characters.values())

        except Exception as e:
            logger.error(f"Character extraction error: {e}")
            return []

    async def _analyze_relationships(
        self,
        novel_id: str,
        characters: List[Dict],
        chapters: List[Dict],
        depth: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict]:
        """Analyze relationships between characters"""
        sample_size = {"quick": 3, "standard": 10, "deep": len(chapters)}[depth]
        sampled_chapters = chapters[:sample_size]

        combined_text = "\n\n".join(
            [f"【{ch['title']}】\n{ch['content'][:2000]}" for ch in sampled_chapters]
        )

        try:
            relationships = await self.llm.analyze_relationships(
                characters, combined_text, provider=provider, model=model
            )

            # Create name/alias to ID mapping for smarter matching
            name_map = {}
            for c in characters:
                c_id = c["id"]
                # Map full name
                name_map[c["name"]] = c_id
                # Map aliases
                if "aliases" in c and isinstance(c["aliases"], list):
                    for alias in c["aliases"]:
                        if alias:
                            name_map[alias] = c_id

            result = []
            for rel in relationships:
                source_name = rel.get("source", "")
                target_name = rel.get("target", "")

                # Try to find ID by name or alias
                source_id = name_map.get(source_name)
                target_id = name_map.get(target_name)

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

            # Save relationships to SQLite
            if result:
                async with get_db() as db:
                    for rel in result:
                        await db.execute(
                            """
                            INSERT INTO relationships (id, novel_id, source_id, target_id, type, 
                                                      subtype, description, strength, first_chapter)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                rel["id"],
                                novel_id,
                                rel["source_id"],
                                rel["target_id"],
                                rel["type"],
                                rel.get("subtype"),
                                rel["description"],
                                rel["strength"],
                                rel["first_chapter"],
                            ),
                        )
                    await db.commit()
                logger.info(f"Saved {len(result)} relationships to SQLite database")

            logger.info(f"Processed {len(result)} relationships")
            return result

        except Exception as e:
            logger.error(f"Relationship analysis error: {e}")
            return []

    async def _track_plots(
        self,
        novel_id: str,
        chapters: List[Dict],
        depth: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict]:
        """Track plot developments (placeholder)"""
        # This would involve more complex analysis
        # For now, return empty list
        logger.warning("Plot tracking not fully implemented yet")
        return []

    async def _generate_summaries(
        self,
        novel_id: str,
        chapters: List[Dict],
        depth: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[Dict]:
        """Generate chapter summaries with concurrency control"""
        summaries = []

        # Limit number of summaries based on depth
        max_chapters = {"quick": 5, "standard": 20, "deep": len(chapters)}[depth]
        target_chapters = chapters[:max_chapters]

        logger.info(f"Generating summaries for {len(target_chapters)} chapters")

        # Concurrency control
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

        async def process_chapter(chapter: Dict) -> Optional[Dict]:
            async with semaphore:
                try:
                    summary = await self.llm.generate_summary(
                        chapter["content"], provider=provider, model=model
                    )

                    return {
                        "chapter_id": chapter["id"],
                        "chapter_num": chapter["chapter_num"],
                        "summary": summary,
                    }
                except Exception as e:
                    logger.error(
                        f"Summary generation error for chapter {chapter['chapter_num']}: {e}"
                    )
                    return None

        # Execute tasks concurrently
        tasks = [process_chapter(chapter) for chapter in target_chapters]
        results = await asyncio.gather(*tasks)

        # Filter out failed results
        valid_results = [r for r in results if r is not None]

        # Sort by chapter number to maintain order
        valid_results.sort(key=lambda x: x["chapter_num"])

        # Batch update database
        if valid_results:
            async with get_db() as db:
                await db.executemany(
                    "UPDATE chapters SET summary = ? WHERE id = ?",
                    [(r["summary"], r["chapter_id"]) for r in valid_results],
                )
                await db.commit()
            logger.info(f"Batch updated summaries for {len(valid_results)} chapters")

        return valid_results

    async def _update_progress(self, task_id: str, progress: float, message: Optional[str] = None):
        """Update task progress in database"""
        async with get_db() as db:
            await db.execute(
                "UPDATE analysis_tasks SET progress = ? WHERE id = ?", (progress, task_id)
            )
            await db.commit()
