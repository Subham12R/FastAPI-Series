from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.service import BookService
from src.db.main import get_session

router = APIRouter()
book_service = BookService()

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
async def get_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate, session: AsyncSession = Depends(get_session)
):
    new_book = await book_service.create_book(session, book_data)
    return new_book


@router.get(
    "/{book_uid}",
)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book_by_id(session, book_uid)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_uid}")
async def update_book(
    book_uid: str,
    book_updatedata: BookUpdate,
    session: AsyncSession = Depends(get_session),
):
    book = await book_service.update_book(session, book_uid, book_updatedata)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_uid}", status_code=status.HTTP_200_OK)
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    result = await book_service.delete_book(session, book_uid)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return {"message": "Book deleted successfully!"}
