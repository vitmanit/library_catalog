from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from config.settings import get_settings
from infrastructure.logging.setup import setup_logging
from presentation.api.exception_handlers import register_exception_handlers
from presentation.middleware.logging import log_requests_middleware
from presentation.api.v1 import books, health

settings = get_settings()


def create_application() -> FastAPI:
    """Application factory"""

    # Setup logging
    setup_logging(
        environment=settings.environment,
        log_level=settings.log_level
    )

    # Create appSS
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        debug=settings.debug,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gzip Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Custom middleware
    app.middleware("http")(log_requests_middleware)

    # Exception handlers
    register_exception_handlers(app)

    # Register routers
    app.include_router(
        books.router,
        prefix=f"{settings.api_v1_prefix}/books",
        tags=["Books"]
    )
    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"]
    )

    @app.on_event("startup")
    async def startup_event():
        """Startup tasks"""
        from loguru import logger
        logger.info(
            "application_started",
            environment=settings.environment,
            version=settings.api_version
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown tasks"""
        from loguru import logger
        logger.info("application_shutdown")

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )