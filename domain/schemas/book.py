from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime


class BookCreate(BaseModel):
    """Schema for creating a book"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Book title",
        examples=["The Great Gatsby"]
    )
    author: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Book author",
        examples=["F. Scott Fitzgerald"]
    )
    year_publication: int = Field(
        ...,
        ge=1000,  # >= 1000
        le=datetime.now().year + 1,  # <= next year
        description="Year of publication",
        examples=[1925]
    )
    genre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Book genre",
        examples=["Fiction"]
    )
    number_pages: int = Field(
        ...,
        gt=0,  # > 0
        le=50000,  # <= 50000
        description="Number of pages",
        examples=[180]
    )
    isbn: Optional[str] = Field(
        None,
        pattern=r'^(?:\d{10}|\d{13})$',  # ISBN-10 or ISBN-13
        description="ISBN number (10 or 13 digits)",
        examples=["9780743273565"]
    )
    accessibility: bool = Field(
        default=True,
        description="Book availability status"
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Book description"
    )

    @field_validator('title', 'author')
    @classmethod
    def clean_string(cls, value: str) -> str:
        """Remove extra whitespace"""
        return ' '.join(value.split())

    @field_validator('genre')
    @classmethod
    def validate_genre(cls, value: str) -> str:
        """Validate genre against allowed list"""
        allowed_genres = {
            'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy',
            'Mystery', 'Thriller', 'Romance', 'Horror', 'Biography',
            'History', 'Science', 'Poetry', 'Drama', 'Children'
        }
        cleaned = ' '.join(value.split())
        if cleaned not in allowed_genres:
            raise ValueError(
                f"Genre must be one of: {', '.join(sorted(allowed_genres))}"
            )
        return cleaned

    @model_validator(mode='after')
    def validate_book(self):
        """Cross-field validation"""
        # Проверка логики дат
        current_year = datetime.now().year
        if self.year_publication > current_year:
            # Если книга из будущего, она не может быть доступна
            if self.accessibility:
                raise ValueError(
                    "Books from future cannot be marked as accessible"
                )

        return self


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    year_publication: Optional[int] = Field(
        None,
        ge=1000,
        le=datetime.now().year + 1
    )
    genre: Optional[str] = Field(None, min_length=1, max_length=100)
    number_pages: Optional[int] = Field(None, gt=0, le=50000)
    isbn: Optional[str] = Field(None, pattern=r'^(?:\d{10}|\d{13})$')
    accessibility: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator('title', 'author')
    @classmethod
    def clean_string(cls, value: Optional[str]) -> Optional[str]:
        if value:
            return ' '.join(value.split())
        return value


class BookResponse(BookCreate):
    """Schema for book response"""
    book_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [{
                "book_id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "year_publication": 1925,
                "genre": "Fiction",
                "number_pages": 180,
                "isbn": "9780743273565",
                "accessibility": True,
                "description": "A novel about the American Dream",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }]
        }
    }