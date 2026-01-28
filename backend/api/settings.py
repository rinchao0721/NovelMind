"""
Settings API endpoints
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.settings_service import get_settings_service
from services.llm_service import LLMService
from utils.logger import get_log_file_path

router = APIRouter()


class LLMTestRequest(BaseModel):
    """LLM connection test request"""

    provider: str
    config: Dict[str, Any]


class Neo4jTestRequest(BaseModel):
    """Neo4j connection test request"""

    uri: str
    user: str
    password: str


@router.get("")
async def get_settings():
    """Get all settings"""
    settings_service = get_settings_service()
    settings = await settings_service.load_settings()
    return settings


@router.post("")
async def save_settings(data: Dict[str, Any]):
    """Save all settings"""
    settings_service = get_settings_service()
    await settings_service.save_settings(data)
    return {"success": True, "message": "Settings saved successfully"}


@router.post("/test-provider")
async def test_provider(request: LLMTestRequest):
    """Test LLM provider connection"""
    try:
        llm_service = LLMService()
        success = await llm_service.test_connection(
            provider=request.provider, config=request.config
        )

        if not success:
            logging.error(f"Connection test failed for provider: {request.provider}")

        return {
            "success": success,
            "error": None if success else "Connection test failed (check logs for details)",
        }
    except Exception as e:
        logging.error(f"Error testing provider {request.provider}: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/test-neo4j")
async def test_neo4j(request: Neo4jTestRequest):
    """Test Neo4j database connection"""
    try:
        from database.neo4j_db import Neo4jDB

        neo4j = Neo4jDB(uri=request.uri, user=request.user, password=request.password)

        success = await neo4j.test_connection()
        await neo4j.close()

        return {
            "success": success,
            "error": None if success else "Connection test failed",
        }
    except ImportError:
        return {"success": False, "error": "Neo4j driver not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/logs")
async def get_logs(lines: int = Query(500, ge=1, le=5000)):
    """Get application logs"""
    try:
        log_file = get_log_file_path()
        if not log_file.exists():
            return {"logs": []}

        # Read last N lines efficiently
        # Since files can be large, we read the whole file if small,
        # or use a buffer from the end if large.
        # For simplicity given the line limit, readlines() is usually fine for < 10MB logs
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()

        return {"logs": all_lines[-lines:]}
    except Exception as e:
        logging.error(f"Failed to read logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to read logs")


@router.delete("/logs")
async def clear_logs():
    """Clear application logs"""
    try:
        log_file = get_log_file_path()
        # Truncate file
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("")
        return {"success": True}
    except Exception as e:
        logging.error(f"Failed to clear logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear logs")
