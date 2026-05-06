import uuid
from datetime import date, datetime

from pydantic import BaseModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookUpdate(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
