from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Boolean

Base = declarative_base()

class Book(Base):
    __tablename__ = "Books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year_publication = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    number_pages = Column(Integer, nullable=False)
    accessibility = Column(Boolean(), default=True)
