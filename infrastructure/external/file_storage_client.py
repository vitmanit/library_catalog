import asyncio
import aiofiles
import json
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class FileStorageClient:
    def __init__(self, file_path: str = "books.json"):
        self.file_path = Path(file_path)

    async def append_book_async(self, book_dict: Dict[str, Any]) -> None:
        """Асинхронная запись в файл"""
        # Читаем существующие книги
        if self.file_path.exists():
            async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                books = json.loads(content) if content else []
        else:
            books = []

        # Добавляем новую книгу
        books.append(book_dict)

        # Записываем обратно
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(books, ensure_ascii=False, indent=2))
        logger.info(f"Book appended to {self.file_path}")

    # Можно добавить методы для чтения, удаления и т.д.
    # async def get_books_async(self) -> list:
    #     ...
    # async def remove_book_async(self, book_id: int) -> None:
    #     ...