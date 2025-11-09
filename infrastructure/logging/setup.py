import logging
import sys
from loguru import logger


def setup_logging(environment: str, log_level: str):
    """Setup structured logging"""

    # Remove default handlers
    logger.remove()

    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # File logging
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Новый файл каждый день
        retention="30 days",  # Хранить 30 дней
        compression="zip",  # Сжимать старые логи
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        serialize=False
    )

    # JSON logging for production
    if environment == "production":
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.json",
            rotation="00:00",
            retention="90 days",
            compression="zip",
            level="INFO",
            serialize=True  # JSON format
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )