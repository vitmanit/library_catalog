from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

# Тип-параметр для обобщённой (generic) модели
T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Обобщённая (Generic) схема для ответа с пагинацией.
    Позволяет возвращать список элементов вместе с метаданными пагинации.
    """
    items: List[T] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Номер текущей страницы (1-индексированная)")
    page_size: int = Field(..., description="Количество элементов на странице")
    total_pages: int = Field(..., description="Общее количество страниц")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        # Примеры элементов типа T (например, BookResponse)
                        # {
                        #     "book_id": 1,
                        #     "title": "Example Book",
                        #     ...
                        # }
                    ],
                    "total": 100,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 5
                }
            ]
        }
    }