from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    year_publication: int
    genre: str
    number_pages: int
    accessibility: bool = True

class BookResponse(BookCreate):
    book_id: int

    class Config:
        from_attributes = True