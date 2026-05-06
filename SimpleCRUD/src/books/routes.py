from typing import List

from fastapi import APIRouter, HTTPException, status

from src.books.book_data import books
from src.books.schemas import Book, BookUpdate

router = APIRouter()

# What is CRUD? CRUD stands for Create, Read, Update, Delete
# Create: Create a new resource
# Read: Read an existing resource
# Update: Update an existing resource
# Delete: Delete an existing resource

# What is a resource?
# A resource is a representation of a real-world entity, such as a user, a book, or a product

# Basic CRUD operations
# Endpoints                      HTTP Method                Description
# /books                         GET                        Get all books
# /books                         POST                       Create a new book
# /books/{id}                    PATCH                      Update a book by id
# /books/{id}                    DELETE                     Delete a book by id


@router.get("/", response_model=List[Book])
async def get_books():
    return books


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book_data: Book) -> dict:
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book


@router.get(
    "/{id}",
)
async def get_book(id: int) -> dict:
    for book in books:
        if book["id"] == id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@router.patch("/{id}")
async def update_book(id: int, book_updatedata: BookUpdate) -> dict:
    for book in books:
        if book["id"] == id:
            book["title"] = book_updatedata.title
            book["author"] = book_updatedata.author
            book["publisher"] = book_updatedata.publisher
            book["page_count"] = book_updatedata.page_count
            book["language"] = book_updatedata.language
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int):
    for book in books:
        if book["id"] == id:
            books.remove(book)
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
