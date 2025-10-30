from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.connect import get_db
from models.Books import Book
from shemas import BookCreate, BookResponse
from sqlalchemy import select


router_books = APIRouter(prefix='/books', tags=['Books'])

@router_books.post("/", response_model=BookResponse, status_code=201)
async def add_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router_books.get('/{book_id}', response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.book_id == book_id))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail='Book not found')
    return book

@router_books.get("/", response_model=List[BookResponse])
async def get_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return books


