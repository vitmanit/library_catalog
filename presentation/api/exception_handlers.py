from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import traceback
import logging
from domain.exceptions import BookNotFoundException, BookAlreadyExistsException, ExternalServiceException, ValidationException
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers"""

    @app.exception_handler(BookNotFoundException)
    async def book_not_found_handler(
            request: Request,
            exc: BookNotFoundException
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "not_found",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(BookAlreadyExistsException)
    async def book_exists_handler(
            request: Request,
            exc: BookAlreadyExistsException
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "conflict",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
            request: Request,
            exc: ValidationException
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(ExternalServiceException)
    async def external_service_handler(
            request: Request,
            exc: ExternalServiceException
    ):
        logger.error(f"External service error: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "external_service_error",
                "message": "External service temporarily unavailable",
                "details": exc.details if not settings.is_production else {}
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
            request: Request,
            exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
            request: Request,
            exc: IntegrityError
    ):
        logger.error(f"Database integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "database_error",
                "message": "Database constraint violation",
                "details": {} if settings.is_production else {"db_error": str(exc)}
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
            request: Request,
            exc: SQLAlchemyError
    ):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "database_error",
                "message": "Database error occurred",
                "details": {} if settings.is_production else {"db_error": str(exc)}
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
            request: Request,
            exc: Exception
    ):
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "traceback": traceback.format_exc(),
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": {} if settings.is_production else {
                    "error": str(exc),
                    "type": type(exc).__name__
                }
            }
        )