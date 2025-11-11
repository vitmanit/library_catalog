from fastapi import Request
import time
from loguru import logger


async def log_requests_middleware(request: Request, call_next):
    """Log all requests with timing"""

    request_id = request.headers.get('X-Request-ID', 'unknown')
    start_time = time.time()

    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        request_id=request_id,
        client=request.client.host if request.client else None
    )

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{duration:.3f}s",
            request_id=request_id
        )

        response.headers['X-Request-ID'] = request_id
        response.headers['X-Process-Time'] = str(duration)

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration=f"{duration:.3f}s",
            request_id=request_id,
            exc_info=True
        )
        raise