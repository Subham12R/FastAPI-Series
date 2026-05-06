from fastapi import FastAPI

from src.books.routes import router

version = "v1"

app = FastAPI(
    title="Book API",
    description="Web API for managing books",
    version=version,
)

app.include_router(router, prefix=f"/api/{version}/books", tags=["books"])
