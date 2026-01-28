"""
Analysis API endpoints
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from database.sqlite_db import get_db
from services.analysis_engine import AnalysisEngine

router = APIRouter()


class AnalysisConfig(BaseModel):
    """Analysis configuration"""

    novel_id: str
    scope: str = "full"  # full or partial
    chapter_start: Optional[int] = None
    chapter_end: Optional[int] = None
    depth: str = "standard"  # quick, standard, deep
    features: list = ["characters", "relationships", "plot", "summary"]


class AnalysisStatusResponse(BaseModel):
    """Analysis status response"""

    id: str
    novel_id: str
    status: str
    progress: float
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]


class AnalysisResultResponse(BaseModel):
    """Analysis result response"""

    task_id: str
    novel_id: str
    character_count: int
    relationship_count: int
    plot_count: int
    chapter_count: int


# Store running tasks (in production, use Redis or similar)
running_tasks: dict = {}


async def run_analysis(task_id: str, config: AnalysisConfig):
    """Background task to run analysis"""
    try:
        async with get_db() as db:
            # Update status to analyzing
            await db.execute(
                "UPDATE analysis_tasks SET status = 'analyzing', started_at = ? WHERE id = ?",
                (datetime.now().isoformat(), task_id),
            )
            await db.commit()

        # Run analysis engine
        engine = AnalysisEngine()
        await engine.analyze(novel_id=config.novel_id, task_id=task_id, config=config.model_dump())

        async with get_db() as db:
            # Update status to completed
            await db.execute(
                """
                UPDATE analysis_tasks 
                SET status = 'completed', progress = 100, completed_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(), task_id),
            )
            await db.commit()

            # Update novel status
            await db.execute(
                "UPDATE novels SET analysis_status = 'completed', updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), config.novel_id),
            )
            await db.commit()

    except Exception as e:
        async with get_db() as db:
            await db.execute(
                """
                UPDATE analysis_tasks 
                SET status = 'failed', error_message = ?, completed_at = ?
                WHERE id = ?
                """,
                (str(e), datetime.now().isoformat(), task_id),
            )
            await db.commit()

            await db.execute(
                "UPDATE novels SET analysis_status = 'failed' WHERE id = ?", (config.novel_id,)
            )
            await db.commit()
    finally:
        running_tasks.pop(task_id, None)


@router.post("/start", response_model=AnalysisStatusResponse)
async def start_analysis(config: AnalysisConfig, background_tasks: BackgroundTasks):
    """Start a new analysis task"""
    # Validate novel exists
    async with get_db() as db:
        cursor = await db.execute("SELECT id FROM novels WHERE id = ?", (config.novel_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Novel not found")

    # Create analysis task
    task_id = str(uuid.uuid4())

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO analysis_tasks (id, novel_id, status, progress)
            VALUES (?, ?, 'pending', 0)
            """,
            (task_id, config.novel_id),
        )

        # Update novel status
        await db.execute(
            "UPDATE novels SET analysis_status = 'analyzing' WHERE id = ?", (config.novel_id,)
        )
        await db.commit()

    # Start background task
    running_tasks[task_id] = True
    background_tasks.add_task(run_analysis, task_id, config)

    return AnalysisStatusResponse(
        id=task_id,
        novel_id=config.novel_id,
        status="pending",
        progress=0,
        started_at=None,
        completed_at=None,
        error_message=None,
    )


@router.get("/{task_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(task_id: str):
    """Get the status of an analysis task"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, novel_id, status, progress, started_at, completed_at, error_message
            FROM analysis_tasks WHERE id = ?
            """,
            (task_id,),
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Analysis task not found")

        return AnalysisStatusResponse(
            id=row[0],
            novel_id=row[1],
            status=row[2],
            progress=row[3],
            started_at=row[4],
            completed_at=row[5],
            error_message=row[6],
        )


@router.get("/{task_id}/result", response_model=AnalysisResultResponse)
async def get_analysis_result(task_id: str):
    """Get the result of a completed analysis"""
    async with get_db() as db:
        # Get task info
        cursor = await db.execute(
            "SELECT novel_id, status FROM analysis_tasks WHERE id = ?", (task_id,)
        )
        row = await cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Analysis task not found")

        novel_id, status = row

        if status != "completed":
            raise HTTPException(status_code=400, detail=f"Analysis not completed. Status: {status}")

        # Get counts
        char_cursor = await db.execute(
            "SELECT COUNT(*) FROM characters WHERE novel_id = ?", (novel_id,)
        )
        character_count = (await char_cursor.fetchone())[0]

        chapter_cursor = await db.execute(
            "SELECT COUNT(*) FROM chapters WHERE novel_id = ?", (novel_id,)
        )
        chapter_count = (await chapter_cursor.fetchone())[0]

        # For relationships, we'd query Neo4j in production
        relationship_count = 0
        plot_count = 0

        return AnalysisResultResponse(
            task_id=task_id,
            novel_id=novel_id,
            character_count=character_count,
            relationship_count=relationship_count,
            plot_count=plot_count,
            chapter_count=chapter_count,
        )


@router.post("/{task_id}/cancel")
async def cancel_analysis(task_id: str):
    """Cancel a running analysis task"""
    if task_id in running_tasks:
        running_tasks.pop(task_id)

    async with get_db() as db:
        await db.execute("UPDATE analysis_tasks SET status = 'cancelled' WHERE id = ?", (task_id,))
        await db.commit()

    return {"message": "Analysis cancelled"}
