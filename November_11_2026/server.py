import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(current_dir.parent) not in sys.path:
    sys.path.insert(1, str(current_dir.parent))

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import  engine
from routers import todos, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the API. Documentation is available at /docs"}


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(todos.router, prefix="/todos", tags=["todos"])
