"""
Settings API endpoints
"""

import json
from typing import Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from services.settings_service import get_settings_service
from services.llm_service import LLMService

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

        return {
            "success": success,
            "error": None if success else "Connection test failed",
        }
    except Exception as e:
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
