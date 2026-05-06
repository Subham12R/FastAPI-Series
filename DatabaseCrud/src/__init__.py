from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.books.routes import router
from src.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Server is starting....")
    await init_db()
    yield
    print(f"Server is stopped")


version = "v1"

app = FastAPI(
    title="Book API",
    description="Web API for managing books",
    version=version,
    lifespan=lifespan,
)

app.include_router(router, prefix=f"/api/{version}/books", tags=["books"])
