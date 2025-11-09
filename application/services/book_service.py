from typing import List, Optional
from fastapi import Depends
from domain.repositories.book_repository import IBookRepository
from domain.schemas.book import BookCreate, BookResponse
from infrastructure.external.openlibrary_client import OpenLibraryClient
from infrastructure.external.jsonbin_client import JsonBinClient
from infrastructure.repositories.book_repository import get_book_repository


class BookService:
    def __init__(
            self,
            repository: IBookRepository,
            openlibrary_client: Optional[OpenLibraryClient] = None,
            jsonbin_client: Optional[JsonBinClient] = None
    ):
        self.repository = repository
        self.openlibrary_client = openlibrary_client
        self.jsonbin_client = jsonbin_client

    async def get_book(self, book_id: int) -> BookResponse:
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found")
        return BookResponse.model_validate(book)

    async def get_books(
            self,
            author: Optional[str] = None,
            genre: Optional[str] = None,
            year_publication: Optional[int] = None
    ) -> List[BookResponse]:
        filters = {
            'author': author,
            'genre': genre,
            'year_publication': year_publication
        }
        books = await self.repository.get_all(filters)
        return [BookResponse.model_validate(book) for book in books]

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        # Создаем книгу в БД
        book = await self.repository.create(book_data)

        # Опционально: получаем доп. информацию
        if self.openlibrary_client:
            try:
                extra_info = await self.openlibrary_client.search(book_data.title)
                # Можно обновить книгу дополнительной информацией
            except Exception as e:
                # Логируем, но не падаем
                print(f"Failed to fetch extra info: {e}")

        # Опционально: сохраняем в JSONBin
        if self.jsonbin_client:
            try:
                await self.jsonbin_client.save(book_data.model_dump())
            except Exception as e:
                print(f"Failed to save to JSONBin: {e}")

        return BookResponse.model_validate(book)

    async def update_book(self, book_id: int, book_data: BookCreate) -> BookResponse:
        book = await self.repository.update(book_id, book_data)
        return BookResponse.model_validate(book)

    async def delete_book(self, book_id: int) -> BookResponse:
        book = await self.repository.delete(book_id)
        return BookResponse.model_validate(book)


def get_book_service(
        repository: IBookRepository = Depends(get_book_repository)
) -> BookService:
    return BookService(repository)