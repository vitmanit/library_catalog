from abc import ABC, abstractmethod

class BaseApiClient(ABC):
    @abstractmethod
    async def get(self, url: str, **kwargs):
        pass

    @abstractmethod
    async def post(self, url: str, data=None, **kwargs):
        pass