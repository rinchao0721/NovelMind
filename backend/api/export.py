"""
Export API endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from services.export_service import get_export_service

router = APIRouter()


@router.get("/{novel_id}/json")
async def export_json(novel_id: str):
    """Export analysis results as JSON"""
    try:
        export_service = get_export_service()
        json_content = await export_service.export_json(novel_id)

        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{novel_id}_analysis.json"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{novel_id}/markdown")
async def export_markdown(novel_id: str):
    """Export analysis results as Markdown"""
    try:
        export_service = get_export_service()
        md_content = await export_service.export_markdown(novel_id)

        return Response(
            content=md_content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{novel_id}_analysis.md"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{novel_id}/data")
async def get_export_data(novel_id: str):
    """Get exportable data as JSON response (not download)"""
    try:
        export_service = get_export_service()
        data = await export_service.get_novel_data(novel_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
