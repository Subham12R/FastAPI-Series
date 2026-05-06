from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from .models import Book
from .schemas import BookCreate, BookUpdate


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)
        return result.all()

    async def get_book_by_id(self, session: AsyncSession, book_uid: str):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        return result.first()

    async def create_book(self, session: AsyncSession, book_data: BookCreate):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data.published_date, "%Y-%m-%d"
        )
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, session: AsyncSession, book_uid: str, update_data: BookUpdate
    ):
        book_to_update = await self.get_book_by_id(session, book_uid)
        if book_to_update is None:
            return None

        update_data_dict = update_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(book_to_update, k, v)

        await session.commit()
        return book_to_update

    async def delete_book(self, session: AsyncSession, book_uid: str):
        book_to_delete = await self.get_book_by_id(session, book_uid)
        if book_to_delete is None:
            return None

        await session.delete(book_to_delete)
        await session.commit()
        return {}
