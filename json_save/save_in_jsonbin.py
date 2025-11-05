import httpx
import asyncio

from HTTP_REQUEST.BaseApi import BaseApiClient
from api import Books

class JsobinCient(BaseApiClient):
    def __init__(self, api_key: str):
        self.base_url = 'https://api.jsonbin.io/v3/b'
        self.headers = {
            'X-Master-Key': api_key,
            'Content-Type': 'application/json'
        }

    #Получить книгу
    async def get(self, bin_id: str, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url + f'/{bin_id}', headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    #Создать книгу
    async def post(self, data=None, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=self.headers, json=data, **kwargs)
            response.raise_for_status()
            return response.json()

jsobin = JsobinCient(api_key='$2a$10$Jnw1/tH1QXgtCxLp3fQfiO9h5.gQ34dILvwn9Yk96eiDZOcttQI4y')