from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import connections
from tortoise.contrib.fastapi import register_tortoise

from app.api.ask import router as ask_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.core.config import TORTOISE_ORM
from app.core.config import settings
from app.core.logging import get_logger

app = FastAPI(title="Cyberify KB")
logger = get_logger(__name__)

logger.info("FastAPI application initializing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(ask_router)


@app.on_event("startup")
async def create_vector_extension() -> None:
    connection = connections.get("default")
    try:
        logger.info("Ensuring pgvector extension exists")
        await connection.execute_script("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("pgvector extension ready")
    except Exception:
        logger.warning(
            "pgvector extension unavailable; using double precision[] embeddings and in-app similarity"
        )
