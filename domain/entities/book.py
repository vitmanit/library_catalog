from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=False)
    year_publication = Column(Integer, nullable=False)
    genre = Column(String(100), nullable=False)
    number_pages = Column(Integer, nullable=False)
    isbn = Column(String(13), unique=True, nullable=True)
    accessibility = Column(Boolean, default=True, nullable=False)
    description = Column(String(5000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('year_publication >= 1000', name='check_year_min'),
        CheckConstraint('year_publication <= 2100', name='check_year_max'),
        CheckConstraint('number_pages > 0', name='check_pages_positive'),
        CheckConstraint('number_pages <= 50000', name='check_pages_max'),
        Index('idx_author_title', 'author', 'title'),
        Index('idx_genre_year', 'genre', 'year_publication'),
        Index('idx_accessibility', 'accessibility'),
    )

    def __repr__(self):
        return f"<Book(id={self.book_id}, title='{self.title}', author='{self.author}')>"