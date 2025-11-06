from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import Column, String, Integer, Boolean

Base = declarative_base()

class Book(Base):
    __tablename__ = "Books"

    book_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    year_publication: Mapped[int] = mapped_column(nullable=False)
    genre: Mapped[str] = mapped_column(nullable=False)
    number_pages: Mapped[int] = mapped_column(nullable=False)
    accessibility: Mapped[bool] = mapped_column(default=True)
