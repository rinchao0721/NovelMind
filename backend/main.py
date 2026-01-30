"""
NovelMind Backend - FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import novels, analysis, characters, relationships, settings as settings_api, export
from database.sqlite_db import init_db


from utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger = setup_logger()
    logger.info("Starting NovelMind Backend...")
    await init_db()
    logger.info(f"Database initialized at: {settings.DATABASE_PATH}")
    yield
    # Shutdown
    logger.info("Shutting down NovelMind Backend...")


app = FastAPI(
    title="NovelMind API",
    description="AI-powered novel plot analysis and character relationship visualization",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development to fix OPTIONS 400 errors
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(novels.router, prefix="/api/novels", tags=["novels"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(relationships.router, prefix="/api/relationships", tags=["relationships"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"name": "NovelMind API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 5001))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug, log_level="info")
