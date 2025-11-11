from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from application.services.book_service import BookService, get_book_service
from domain.schemas.book import BookCreate, BookResponse

router = APIRouter(prefix='/api/v1/books', tags=['Books'])

@router.get('/{book_id}', response_model=BookResponse)
async def get_book(
    book_id: int,
    service: BookService = Depends(get_book_service)
):
    """Получить книгу по ID"""
    try:
        return await service.get_book(book_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/', response_model=List[BookResponse])
async def get_books(
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    year_publication: Optional[int] = Query(None),
    service: BookService = Depends(get_book_service)
):
    """Получить список книг с фильтрацией"""
    return await service.get_books(author, genre, year_publication)


@router.post('/', response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    service: BookService = Depends(get_book_service)
):
    """Создать новую книгу"""
    try:
        return await service.create_book(book)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put('/{book_id}', response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookCreate,
    service: BookService = Depends(get_book_service)
):
    """Обновить книгу"""
    try:
        return await service.update_book(book_id, book_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete('/{book_id}', response_model=BookResponse)
async def delete_book(
    book_id: int,
    service: BookService = Depends(get_book_service)
):
    """Удалить книгу"""
    try:
        return await service.delete_book(book_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))