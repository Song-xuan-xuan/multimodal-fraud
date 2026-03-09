import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.ws.socketio_server import socket_app
from app.db.base import init_db
from app.services.rag_service import warm_rag_in_background

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    setup_logging()
    settings = get_settings()
    logger.info("Starting application (DEBUG=%s)", settings.DEBUG)

    # Ensure directories exist
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.data_path.mkdir(parents=True, exist_ok=True)
    settings.storage_path.mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()

    # Start RAG warm-up in the background to avoid blocking overall app startup.
    warm_rag_in_background()

    yield

    logger.info("Shutting down application")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Fake News Detection Platform",
        description="FastAPI backend for fake news detection, fact-checking, and AI analysis",
        version="2.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router)

    # SocketIO (ASGI mount)
    app.mount("/ws", socket_app)

    # Health check
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
