import httpx
from abc import ABC, abstractmethod
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from config.settings import get_settings
from domain.exceptions import ExternalServiceException

settings = get_settings()

# --- Абстрактный базовый класс ---

class BaseExternalApiClient(ABC):
    """
    Абстрактный базовый класс для всех внешних API-клиентов.
    Определяет общий интерфейс и потенциальную общую логику.
    """

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Проверяет доступность внешнего сервиса.
        Должен быть реализован в подклассе.
        """
        pass

    # Можно добавить и другие абстрактные методы, если они общие для всех клиентов


# --- Базовый класс с общей реализацией ---

class BaseHttpApiClient(BaseExternalApiClient):
    """
    Базовый класс с общей логикой для API-клиентов, использующих HTTP.
    Включает настройку клиента, retry-логику и базовую обработку ошибок.
    """

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        # Общий httpx.AsyncClient может быть инициализирован тут,
        # но часто его лучше создавать в каждом методе, чтобы избежать проблем с жизненным циклом.

    def get_retry_decorator(self, attempts: int = 3):
        """
        Возвращает декоратор retry с заданными параметрами.
        Может быть переопределен в подклассе для настройки под конкретный API.
        """
        return retry(
            stop=stop_after_attempt(attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
            reraise=True
        )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Внутренний метод для выполнения HTTP-запросов.
        Инкапсулирует общую логику: создание клиента, отправка, обработка статусов.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        # Добавляем общий таймаут, если не задан явно в kwargs
        kwargs.setdefault('timeout', self.timeout)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)
                # Обработка успешных ответов
                response.raise_for_status()
                return response
        except httpx.TimeoutException as e:
            logger.error(f"Timeout while requesting {method} {url}: {e}")
            raise ExternalServiceException(
                message=f"{self.__class__.__name__} API timeout",
                details={"url": url, "method": method, "error": str(e)}
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP {status_code} error while requesting {method} {url}: {e.response.text}")
            # Можно добавить специфичную обработку кодов (401, 403, 429) в подклассах
            raise ExternalServiceException(
                message=f"{self.__class__.__name__} API error",
                details={
                    "url": url,
                    "method": method,
                    "status_code": status_code,
                    "response_text": e.response.text,
                    "error": str(e)
                }
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while requesting {method} {url}: {e}")
            raise ExternalServiceException(
                message=f"{self.__class__.__name__} API HTTP error",
                details={"url": url, "method": method, "error": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error while requesting {method} {url}: {e}")
            raise ExternalServiceException(
                message=f"{self.__class__.__name__} API unexpected error",
                details={"url": url, "method": method, "error": str(e)}
            )

    # Пример абстрактного метода, который должен быть реализован
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Проверяет доступность внешнего сервиса.
        Пример: выполнить GET-запрос к эндпоинту статуса.
        """
        # Например:
        # response = await self._make_request("GET", "/status")
        # return response.status_code == 200
        pass

# --- Пример использования в подклассе ---

# class OpenLibraryClient(BaseHttpApiClient):
#     def __init__(self):
#         super().__init__(
#             base_url=settings.openlibrary_base_url,
#             timeout=settings.openlibrary_timeout
#         )
#
#     @BaseHttpApiClient.get_retry_decorator(attempts=3) # Используем базовый декоратор
#     async def search(self, title: str) -> dict:
#         response = await self._make_request("GET", "/search.json", params={"title": title})
#         data = response.json()
#         # ... логика обработки ...
#         return data
#
#     async def health_check(self) -> bool:
#         try:
#             response = await self._make_request("GET", "/status.json") # Или другой эндпоинт
#             return response.status_code == 200
#         except ExternalServiceException:
#             return False
#
# class JsonBinClient(BaseHttpApiClient): # <-- Наследуемся от BaseHttpApiClient
#     def __init__(self):
#         # JsonBinClient не обязательно наследуется от BaseHttpApiClient,
#         # но если он использует HTTP, то наследование оправдано.
#         # Важно передать нужные параметры, например, API-ключ в заголовках.
#         super().__init__(base_url='https://api.jsonbin.io/v3/b')
#         self.api_key = settings.jsonbin_api_key
#
#     @BaseHttpApiClient.get_retry_decorator(attempts=2)
#     async def save(self, data: dict) -> dict:
#         headers = {'X-Master-Key': self.api_key, 'Content-Type': 'application/json'}
#         response = await self._make_request("POST", "", headers=headers, json=data)
#         return response.json()
#
#     async def health_check(self) -> bool:
#         # Простая проверка - можно ли выполнить запрос (например, получить список бинов)
#         try:
#             # Это просто пример, реальный эндпоинт healthcheck для JSONBin может отличаться
#             response = await self._make_request("GET", "/status", headers={'X-Master-Key': self.api_key})
#             return response.status_code == 200
#         except ExternalServiceException:
#             return False
