from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager # db

from database import engine
from routes import documents, import_jobs


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message:": "Hello World!!"}


app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(import_jobs.router, prefix="/catalogue", tags=["jobs"])

# Validation error

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation failed",
            "errors": exc.errors(),
            "path": str(request.url),
            "headers": dict(request.headers)
        }
    )



# 404 response
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "path": str(request.url)
        }
    )