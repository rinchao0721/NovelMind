# NovelMind Backend

Python FastAPI backend for NovelMind - AI-powered novel analysis engine.

## Features

- File parsing (TXT, DOCX, EPUB, MOBI)
- AI-powered character extraction
- Relationship analysis
- Plot tracking
- Multi-LLM support

## Setup

```bash
# Install dependencies
uv sync

# Run server
uv run python main.py
```

## API Endpoints

- `POST /api/novels/import` - Import a novel
- `GET /api/novels` - List novels
- `POST /api/analysis/start` - Start analysis
- `GET /api/characters` - Get characters
- `GET /api/settings` - Get settings
