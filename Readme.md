# BackendSeries — FastAPI Learning Journey

> A living document tracking my progress from zero to production-ready FastAPI. Every bug, every fix, every "aha!" moment is recorded here so I never forget.

---

## 🚀 Quick Start

Copy-paste these commands to get the `DatabaseCrud` project running from scratch.

```bash
# 1. Activate virtual environment (PowerShell)
env\Scripts\Activate.ps1

# 2. Ensure dependencies are installed
pip install -r DatabaseCrud\requirements.txt

# 3. Start PostgreSQL service (if not running)
# Check: Get-Service -Name "postgresql*"
# Start: Start-Service -Name "postgresql-x64-18"

# 4. Create .env file inside DatabaseCrud/ (see template below)

# 5. Run the server
cd DatabaseCrud
fastapi dev main.py
```

**API Base URL:** `http://localhost:8000/api/v1/books`
**Interactive Docs:** `http://localhost:8000/docs`

---

## 📁 Project Structure

```
BackendSeries/
├── SimpleCRUD/                 # Phase 1: In-memory list (COMPLETED)
│   ├── main.py
│   ├── src/__init__.py
│   └── src/books/
│       ├── routes.py
│       ├── schemas.py
│       └── book_data.py        # Python list acting as "database"
│
├── DatabaseCrud/               # Phase 2: Real PostgreSQL database (ACTIVE)
│   ├── main.py                 # Entry point: from src import app
│   ├── requirements.txt        # fastapi, uvicorn[standard], sqlmodel, asyncpg, pydantic-settings
│   ├── .env                    # DATABASE_URL (ignored by git)
│   ├── .gitignore
│   └── src/
│       ├── __init__.py         # FastAPI app + lifespan (init_db on startup)
│       ├── config.py           # Pydantic Settings (reads .env)
│       ├── db/
│       │   ├── __init__.py
│       │   └── main.py         # Async engine, session factory, get_session()
│       └── books/
│           ├── __init__.py     # Exports router
│           ├── models.py       # SQLModel table definition
│           ├── schemas.py      # Pydantic request/response models
│           ├── routes.py       # FastAPI endpoints (HTTP layer)
│           └── service.py      # Business logic + database queries
│
└── env/                        # Python virtual environment (DO NOT COMMIT)
```

---

## 🏗️ System Architecture

### The Three-Layer Pattern (Industry Standard)

```
┌─────────────────────────────────────────────────────────────┐
│                         HTTP Layer                           │
│                    (routes.py)                               │
│  Receives HTTP requests → Validates input → Returns JSON     │
└──────────────────────────┬──────────────────────────────────┘
                           │ calls
┌──────────────────────────▼──────────────────────────────────┐
│                      Service Layer                           │
│                   (service.py)                               │
│  Business logic → Database queries → Returns models          │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses
┌──────────────────────────▼──────────────────────────────────┐
│                      Database Layer                          │
│                   (models.py + PostgreSQL)                   │
│  SQLModel defines tables → asyncpg talks to PostgreSQL       │
└─────────────────────────────────────────────────────────────┘
```

**Why three layers?** Separation of concerns. You can swap PostgreSQL for MongoDB later and only change `service.py` and `models.py` — `routes.py` stays untouched.

---

## 🗄️ Database Design

### Tech Stack
- **PostgreSQL 18** — The actual database server
- **SQLModel** — ORM that combines SQLAlchemy (database) + Pydantic (validation)
- **asyncpg** — Async PostgreSQL driver (non-blocking, handles many requests)
- **SQLAlchemy Async** — Async engine and session management

### The `Book` Table

```python
# src/books/models.py
import uuid
from datetime import date, datetime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            default=uuid.uuid4,      # NOTE: No ()! Just the function reference
            nullable=False,
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date          # Python date object in DB
    page_count: int
    language: str
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, default=datetime.now())
    )
```

**Key Design Decisions:**
- **`uid` instead of `id`**: UUIDs are globally unique. Safe to expose in URLs, hard to guess.
- **`sa_column=Column(...)`**: Tells SQLModel "this is a database column with these SQL properties."
- **`default=uuid.uuid4` (no parentheses)**: Without `()`, Python stores the function itself. It gets called once per row. With `()`, it would run once when the class is defined — every book would get the same UUID.

---

## 🔌 Connection Flow

### 1. Configuration (`src/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Eager instantiation (current approach — works but crashes if .env is missing)
Config = Settings()
```

**Reads from `.env`:**
```env
DATABASE_URL=postgresql+asyncpg://rikk4:subham9434@localhost:5432/bookly_db
```

**URL Breakdown:**
```
postgresql+asyncpg://  → dialect+driver
rikk4                   → username
:subham9434             → password
@localhost:5432         → host:port
/bookly_db              → database name
```

> ⚠️ **CRITICAL**: If your password contains `@`, `:`, `/`, `?`, `#`, or `&`, you MUST URL-encode it or change it. `@` breaks the URL because it's the separator between credentials and host.

### 2. Engine & Sessions (`src/db/main.py`)

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing_extensions import AsyncGenerator
from src.config import Config

# The engine is the "factory" that connects to PostgreSQL
engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True,              # Logs every SQL query to console (great for learning)
)

# Creates tables on startup (called in lifespan)
async def init_db():
    async with engine.begin() as conn:
        from src.books.models import Book
        await conn.run_sync(SQLModel.metadata.create_all)
        # NOTE: create_all is IDEMPOTENT — safe to run multiple times.
        # If tables exist, it skips them silently.

# Session factory: creates a new session per request
Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,        # MUST be SQLModel's AsyncSession (has .exec())
    expire_on_commit=False,     # Keeps objects accessible after commit
)

# FastAPI Dependency: yields a session, then closes it automatically
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session
```

### 3. Lifespan — Database Startup (`src/__init__.py`)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.books.routes import router
from src.db.main import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting....")
    await init_db()         # Create tables before first request
    yield
    print("Server is stopped")

app = FastAPI(
    title="Book API",
    description="Web API for managing books",
    version="v1",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/books", tags=["books"])
```

---

## 📐 Schemas: Request vs Response

```python
# src/books/schemas.py
from datetime import date, datetime
from pydantic import BaseModel
import uuid

# RESPONSE model (what the API sends back)
class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date       # MUST match the model type!
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

# CREATE request (what the client sends to make a new book)
class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str        # Client sends "YYYY-MM-DD" string
    page_count: int
    language: str

# UPDATE request (what the client sends to modify a book)
class BookUpdate(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    # NOTE: published_date is intentionally omitted here (design choice)
```

**The Golden Rule:**
- The database `model` and the response `schema` must have **matching types**.
- If `models.py` says `published_date: date`, then `schemas.py` `Book` response must also say `date`.
- `BookCreate` can accept a `str` because we convert it to `date` inside the service layer.

---

## 🛣️ API Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/books/` | List all books | — | `List[Book]` |
| POST | `/api/v1/books/` | Create a book | `BookCreate` | `Book` |
| GET | `/api/v1/books/{book_uid}` | Get one book | — | `Book` |
| PATCH | `/api/v1/books/{book_uid}` | Update a book | `BookUpdate` | `Book` |
| DELETE | `/api/v1/books/{book_uid}` | Delete a book | — | `{"message": "..."}` |

---

## 🧠 Key Concepts Explained

### CRUD → HTTP Mapping
| Operation | HTTP Method | SQL Action |
|-----------|-------------|------------|
| Create | POST | INSERT |
| Read | GET | SELECT |
| Update | PATCH | UPDATE |
| Delete | DELETE | DELETE |

### Why Async?
- Traditional Python is **synchronous** — one request at a time per thread.
- **Async** (`async`/`await`) lets one thread handle thousands of requests.
- `asyncpg` is an async PostgreSQL driver. If you use `psycopg2` with async code, it blocks everything.

### Session Lifecycle
```
Request arrives
    ↓
FastAPI calls Depends(get_session)
    ↓
New AsyncSession created (database connection opened)
    ↓
Route handler runs (queries execute)
    ↓
Response sent
    ↓
Session automatically closed (connection returned to pool)
```

**Never share sessions between requests.** Each request gets its own.

### SQLModel's `.exec()` vs SQLAlchemy's `.execute()`
- `session.execute(statement)` → Returns raw SQL rows (tuples). FastAPI can't validate them.
- `session.exec(statement)` → Returns actual model instances. FastAPI validates them as Pydantic models.
- **Always use `.exec()` when working with SQLModel schemas.**

---

## 🐛 The Bug Log — Our Shared Memory

Every error we hit, why it happened, and exactly how we fixed it.

| # | Error Message | Root Cause | The Fix |
|---|---------------|------------|---------|
| 1 | `Could not find a default file to run` | `fastapi dev` needs `main.py` at root | Created `main.py` with `from src import app` |
| 2 | `ModuleNotFoundError: No module named 'book_data'` | Relative import `from book_data` fails from root | Changed to absolute: `from src.books.book_data import ...` |
| 3 | `ValidationError: DATABASE_URL field required` | `.env` file missing or not found | Created `DatabaseCrud/.env` with `DATABASE_URL=...` |
| 4 | `socket.gaierror: getaddrinfo failed` | Password contained `@` which broke the URL | Changed password to remove `@` or URL-encoded it (`%40`) |
| 5 | `AsyncSession has no attribute 'exec'` | Imported `AsyncSession` from `sqlalchemy.ext.asyncio` | Changed import to `sqlmodel.ext.asyncio.session.AsyncSession` **everywhere** |
| 6 | `ResponseValidationError: missing` | Used `session.execute()` which returns tuples, not models | Changed to `session.exec()` in service layer |
| 7 | `ResponseValidationError: published_date string_type` | `schemas.py` said `str`, database returned `date` object | Changed `published_date: str` → `published_date: date` in `Book` schema |
| 8 | `AttributeError: 'coroutine' object has no attribute 'first'` | Forgot `await` when calling `get_book_by_id` inside service | Added `await self.get_book_by_id(...)` |
| 9 | `TypeError: get_book_by_id() takes 2 positional args but 3 given` | Wrong argument order in service call | Fixed: `(session, book_uid)` not `(book_uid, session)` |
| 10 | `__tablename__ declared_attr` warning | VS Code type checker doesn't understand SQLAlchemy metaclass | Added `# type: ignore` or used `ClassVar[str]` |
| 11 | Tables not showing `CREATE TABLE` in logs | `create_all` is idempotent — tables already existed | Dropped table with `DROP TABLE books;` to see creation logs |
| 12 | `psql not recognized` | PostgreSQL `bin` folder not in Windows PATH | Used full path or added `C:\Program Files\PostgreSQL\18\bin` to PATH |
| 13 | `uuid.uuid4()` all same value | Called function at class definition time | Changed to `uuid.uuid4` (pass function, not result) |
| 14 | `Field(Column(...))` not creating columns | First positional arg to `Field()` is `default`, not `sa_column` | Changed to `Field(sa_column=Column(...))` |
| 15 | `AsyncEngine(create_engine(...))` unstable | `create_engine` is sync, doesn't play well with `asyncpg` | Used `create_async_engine()` from SQLAlchemy |
| 16 | `TypeError: create_book() got multiple values for 'session'` | Wrong argument order when calling service from route | Fixed: `book_service.create_book(session, book_data)` |

---

## ⚙️ Environment Setup Reference

### PostgreSQL Commands

```bash
# Check if PostgreSQL is running
Get-Service -Name "postgresql*"

# Start PostgreSQL
Start-Service -Name "postgresql-x64-18"

# Connect as postgres superuser
psql -U postgres

# Connect as your user
psql -U rikk4 -d bookly_db

# Inside psql:
\l              # List databases
\dt             # List tables
\d books        # Describe table structure
\q              # Quit
```

### Virtual Environment

```bash
# Create (if needed)
python -m venv env

# Activate (PowerShell)
env\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Adding PostgreSQL to PATH (Permanent)

```powershell
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\PostgreSQL\18\bin",
    "User"
)
# Restart terminal after running this
```

---

## 📝 .env Template

Create this file at `DatabaseCrud/.env` (never commit it!):

```env
# PostgreSQL Connection URL
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
# 
# WARNING: If your password contains @ : / ? # or &, you MUST change it
# or URL-encode the special characters.
# Example: @ → %40, : → %3A
#
DATABASE_URL=postgresql+asyncpg://rikk4:yourpassword@localhost:5432/bookly_db
```

---

## 🎯 Next Learning Goals

- [ ] Add user authentication (OAuth2 / JWT)
- [ ] Add pagination to GET /books/
- [ ] Add filtering (search by title, author)
- [ ] Add database migrations with Alembic
- [ ] Write automated tests with pytest and TestClient
- [ ] Dockerize the application
- [ ] Deploy to a cloud provider (Render, Railway, AWS)

---

## 💡 Golden Rules (Don't Forget These!)

1. **`session.exec()` not `session.execute()`** when using SQLModel response models.
2. **Import `AsyncSession` from `sqlmodel.ext.asyncio.session`** everywhere — routes, service, and db/main.py.
3. **Schema types must match model types** for response validation.
4. **`create_all` is safe to run repeatedly** — it only creates missing tables.
5. **No `@` in database passwords** unless URL-encoded.
6. **`uuid.uuid4` not `uuid.uuid4()`** in model defaults.
7. **`sa_column=` is required** when passing `Column(...)` to `Field()`.
8. **Each request gets its own session** via `Depends(get_session)`.

---

*Last updated: 2026-05-06*
*Current phase: DatabaseCrud with PostgreSQL + SQLModel*
