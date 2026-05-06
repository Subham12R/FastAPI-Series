from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing_extensions import AsyncGenerator

from src.config import Config

engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True,
)


async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book

        await conn.run_sync(SQLModel.metadata.create_all)


Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session
