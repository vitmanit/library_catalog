from abc import ABC, abstractmethod
from loguru import logger

class BaseApiClient(ABC):
    def log_error(self, msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        logger.info(msg, *args, **kwargs)

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def post(self, *args, data=None, **kwargs):
        pass