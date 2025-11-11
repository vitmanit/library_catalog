import httpx
from loguru import logger

from domain.BaseApi import BaseApiClient


class JsobinCient(BaseApiClient):
    def __init__(self, api_key: str):
        self.base_url = 'https://api.jsonbin.io/v3/b'
        self.headers = {
            'X-Master-Key': api_key,
            'Content-Type': 'application/json'
        }
        logger.info('JsobinCient initialized')

    #Получить книгу
    async def get(self, bin_id: str, **kwargs):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url + f'/{bin_id}', headers=self.headers, **kwargs)
                response.raise_for_status()
                self.log_info(f"GET успешно: bin_id={bin_id}")
                return response.json()
        except Exception as e:
            self.log_error(f'Ошибка в get(bit_id={bin_id}): {e}')
            raise

    #Создать книгу
    async def post(self, data=None, **kwargs):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, headers=self.headers, json=data, **kwargs)
                response.raise_for_status()
                self.log_info(f'POST успешно выполнен, Bin_id = {response.json().get('metadata').get('id')}')
                return response.json()
        except Exception as e:
            self.log_error(f"Ошибка в post(data={data}): {e}")
            raise

jsobin = JsobinCient(api_key='$2a$10$Jnw1/tH1QXgtCxLp3fQfiO9h5.gQ34dILvwn9Yk96eiDZOcttQI4y')
