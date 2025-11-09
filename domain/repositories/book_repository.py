from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.book import Book
from domain.schemas.book import BookCreate


class IBookRepository(ABC):
    @abstractmethod
    async def get_by_id(self, book_id: int) -> Optional[Book]:
        pass

    @abstractmethod
    async def get_all(self, filters: dict) -> List[Book]:
        pass

    @abstractmethod
    async def create(self, book_data: BookCreate) -> Book:
        pass

    @abstractmethod
    async def update(self, book_id: int, book_data: BookCreate) -> Book:
        pass

    @abstractmethod
    async def delete(self, book_id: int) -> Book:
        pass