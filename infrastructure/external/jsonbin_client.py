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


class JsonBinClient:
    def __init__(self):
        # Используем API-ключ из настроек
        self.api_key = settings.jsonbin_api_key
        self.base_url = 'https://api.jsonbin.io/v3/b'
        self.timeout = 30 # Таймаут для JSONBin, можно вынести в настройки

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True
    )
    async def save(self, data: dict) -> dict:
        """
        Сохраняет словарь данных на JSONBin.io.
        Использует retry для повторных попыток при ошибках.
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Master-Key': self.api_key, # Ключ для аутентификации
            # 'X-Collection-Id': 'your_collection_id', # Если используете коллекции
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # POST-запрос для создания новой записи
                response = await client.post(
                    self.base_url,
                    json=data,
                    headers=headers
                )
                response.raise_for_status() # Возбуждает исключение для 4xx/5xx
                result = response.json()

                logger.info(f"Data successfully saved to JSONBin with ID: {result.get('id')}")
                return result

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while saving data to JSONBin: {e}")
            raise ExternalServiceException(
                message="JSONBin API timeout",
                details={"error": str(e)}
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP {status_code} error while saving data to JSONBin: {e.response.text}")
            if status_code == 401:
                raise ExternalServiceException(
                    message="JSONBin API authentication failed (401)",
                    details={"error": "Invalid API key", "status_code": status_code}
                )
            elif status_code == 403:
                 raise ExternalServiceException(
                    message="JSONBin API access forbidden (403)",
                    details={"error": "Access forbidden", "status_code": status_code}
                )
            else:
                raise ExternalServiceException(
                    message="JSONBin API error",
                    details={
                        "status_code": status_code,
                        "response_text": e.response.text,
                        "error": str(e)
                    }
                )
        except Exception as e:
            logger.error(f"Unexpected error while saving data to JSONBin: {e}")
            raise ExternalServiceException(
                message="JSONBin API unexpected error",
                details={"error": str(e)}
            )

# --- Зависимость для DI ---
def get_jsonbin_client() -> JsonBinClient:
    # Проверяем, установлен ли API-ключ, например, через настройки
    if settings.jsonbin_api_key and settings.jsonbin_api_key != "your_api_key_here":
        return JsonBinClient()
    return None # Или бросить ошибку, если клиент обязателен