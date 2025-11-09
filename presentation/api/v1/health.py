from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from config.settings import get_settings
from presentation.api.dependencies import get_db

# Используем настройки, например, для получения версии API или окружения
settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """
    Общий эндпоинт проверки состояния приложения.
    Возвращает статус 'healthy', версию и окружение.
    """
    return {
        "status": "healthy",
        "version": settings.api_version,
        "environment": settings.environment,
        "service": "library-catalog-api"
    }

@router.get("/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт проверки состояния подключения к базе данных.
    Выполняет простой SQL-запрос для проверки соединения.
    """
    try:
        # Выполняем простой запрос к БД
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        # Если возникла ошибка, возвращаем 503 Service Unavailable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {str(e)}"
        )