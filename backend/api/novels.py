"""
Novel management API endpoints
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel

from database.sqlite_db import get_db
from services.file_parser import FileParser
from models.novel import Novel, NovelCreate, NovelResponse

router = APIRouter()


class NovelListResponse(BaseModel):
    """Response model for novel list"""
    novels: List[NovelResponse]
    total: int


@router.post("/import", response_model=NovelResponse)
async def import_novel(file: UploadFile = File(...)):
    """Import a novel from file"""
    # Validate file type
    allowed_extensions = {'.txt', '.docx', '.epub', '.mobi'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse file
        parser = FileParser()
        parsed_data = await parser.parse(content, file_ext, file.filename)
        
        # Create novel record
        novel_id = str(uuid.uuid4())
        novel = Novel(
            id=novel_id,
            title=parsed_data.get('title', file.filename.rsplit('.', 1)[0]),
            author=parsed_data.get('author'),
            file_path=file.filename,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            analysis_status='pending',
            total_chapters=len(parsed_data.get('chapters', [])),
            total_words=parsed_data.get('total_words', 0)
        )
        
        # Save to database
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO novels (id, title, author, file_path, created_at, updated_at, 
                                   analysis_status, total_chapters, total_words)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (novel.id, novel.title, novel.author, novel.file_path,
                 novel.created_at.isoformat(), novel.updated_at.isoformat(),
                 novel.analysis_status, novel.total_chapters, novel.total_words)
            )
            
            # Save chapters
            for i, chapter in enumerate(parsed_data.get('chapters', []), 1):
                chapter_id = str(uuid.uuid4())
                await db.execute(
                    """
                    INSERT INTO chapters (id, novel_id, chapter_num, title, content, word_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (chapter_id, novel_id, i, chapter.get('title', f'第{i}章'),
                     chapter.get('content', ''), chapter.get('word_count', 0))
                )
            
            await db.commit()
        
        return NovelResponse.from_orm(novel)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[NovelResponse])
async def get_novels(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get list of all novels"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, title, author, file_path, created_at, updated_at,
                   analysis_status, total_chapters, total_words
            FROM novels
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, skip)
        )
        rows = await cursor.fetchall()
        
        novels = []
        for row in rows:
            novels.append(NovelResponse(
                id=row[0],
                title=row[1],
                author=row[2],
                file_path=row[3],
                created_at=row[4],
                updated_at=row[5],
                analysis_status=row[6],
                total_chapters=row[7],
                total_words=row[8]
            ))
        
        return novels


@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(novel_id: str):
    """Get a specific novel by ID"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, title, author, file_path, created_at, updated_at,
                   analysis_status, total_chapters, total_words
            FROM novels WHERE id = ?
            """,
            (novel_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Novel not found")
        
        return NovelResponse(
            id=row[0],
            title=row[1],
            author=row[2],
            file_path=row[3],
            created_at=row[4],
            updated_at=row[5],
            analysis_status=row[6],
            total_chapters=row[7],
            total_words=row[8]
        )


@router.delete("/{novel_id}")
async def delete_novel(novel_id: str):
    """Delete a novel and all related data"""
    async with get_db() as db:
        # Check if novel exists
        cursor = await db.execute("SELECT id FROM novels WHERE id = ?", (novel_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Novel not found")
        
        # Delete novel (cascades to chapters, characters, etc.)
        await db.execute("DELETE FROM novels WHERE id = ?", (novel_id,))
        await db.commit()
        
        return {"message": "Novel deleted successfully"}


@router.get("/{novel_id}/chapters")
async def get_novel_chapters(novel_id: str):
    """Get all chapters of a novel"""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT id, chapter_num, title, word_count, summary
            FROM chapters
            WHERE novel_id = ?
            ORDER BY chapter_num
            """,
            (novel_id,)
        )
        rows = await cursor.fetchall()
        
        return [
            {
                "id": row[0],
                "chapter_num": row[1],
                "title": row[2],
                "word_count": row[3],
                "summary": row[4]
            }
            for row in rows
        ]
