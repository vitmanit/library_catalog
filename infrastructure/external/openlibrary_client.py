import httpx
from loguru import logger
from config.settings import get_settings
from domain.exceptions import ExternalServiceException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

settings = get_settings()


class OpenLibraryClient:
    def __init__(self):
        self.base_url = settings.openlibrary_base_url
        self.timeout = settings.openlibrary_timeout

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True
    )
    async def search(self, title: str) -> dict:
        """
        Ищет информацию о книге по названию.
        Использует retry для повторных попыток при ошибках.
        """
        url = f"{self.base_url}/search.json"
        params = {"title": title}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()  # Возбуждает исключение для 4xx/5xx
                data = response.json()

                # API OpenLibrary возвращает {"docs": [...]}
                # Возвращаем первый результат или пустой словарь
                docs = data.get("docs", [])
                if docs:
                    return docs[0]  # Возвращаем первую найденную книгу
                else:
                    logger.info(f"No results found for title: {title} on OpenLibrary")
                    return {}  # Или можно бросить исключение, если результат обязателен

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while searching for '{title}' on OpenLibrary: {e}")
            raise ExternalServiceException(
                message="OpenLibrary API timeout",
                details={"title": title, "error": str(e)}
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while searching for '{title}' on OpenLibrary: {e}")
            raise ExternalServiceException(
                message="OpenLibrary API error",
                details={
                    "title": title,
                    "status_code": e.response.status_code if hasattr(e, 'response') else None,
                    "error": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error while searching for '{title}' on OpenLibrary: {e}")
            raise ExternalServiceException(
                message="OpenLibrary API unexpected error",
                details={"title": title, "error": str(e)}
            )

# --- Зависимость для DI ---
def get_openlibrary_client() -> OpenLibraryClient:
    # Проверяем, включён ли клиент, например, через настройки
    if settings.openlibrary_base_url: # Простая проверка, можно усложнить
        return OpenLibraryClient()
    return None # Или бросить ошибку, если клиент обязателен