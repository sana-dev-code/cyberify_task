from fastapi import APIRouter
from tortoise import connections

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    try:
        await connections.get("default").execute_query("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "database": db_status}