import json
from pathlib import Path

BOOKS_PATH = Path("books.json")


def append_book_to_json(book_dict: dict):
    if BOOKS_PATH.exists():
        with open(BOOKS_PATH, "r", encoding="utf-8") as f:
            books = json.load(f)
    else:
        books = []