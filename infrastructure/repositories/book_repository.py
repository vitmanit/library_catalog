from typing import Optional, List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.repositories.book_repository import IBookRepository
from domain.entities.book import Book
from domain.schemas.book import BookCreate
from presentation.api.dependencies import get_db


class BookRepository(IBookRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, book_id: int) -> Optional[Book]:
        result = await self.session.execute(
            select(Book).where(Book.book_id == book_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, filters: dict) -> List[Book]:
        query = select(Book)

        if filters.get('author'):
            query = query.where(Book.author == filters['author'])
        if filters.get('genre'):
            query = query.where(Book.genre == filters['genre'])
        if filters.get('year_publication'):
            query = query.where(Book.year_publication == filters['year_publication'])

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, book_data: BookCreate) -> Book:
        db_book = Book(**book_data.model_dump())
        self.session.add(db_book)
        await self.session.flush()
        await self.session.refresh(db_book)
        return db_book

    async def update(self, book_id: int, book_data: BookCreate) -> Book:
        book = await self.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found")

        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)

        await self.session.flush()
        await self.session.refresh(book)
        return book

    async def delete(self, book_id: int) -> Book:
        book = await self.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found")

        await self.session.delete(book)
        await self.session.flush()
        return book


def get_book_repository(session: AsyncSession = Depends(get_db)) -> IBookRepository:
    return BookRepository(session)