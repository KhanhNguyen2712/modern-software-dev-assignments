from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .responses import error_response
from .routers import action_items as action_items_router
from .routers import notes as notes_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path("data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()
    yield


app = FastAPI(title="Modern Software Dev Starter (Week 5)", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.exception_handler(HTTPException)
async def handle_http_exception(_: object, exc: HTTPException):
    code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return error_response(code=code, message=str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: object, exc: RequestValidationError):
    fields = ", ".join(str(error["loc"][-1]) for error in exc.errors())
    message = f"Invalid request for field(s): {fields}"
    return error_response(code="VALIDATION_ERROR", message=message, status_code=400)


@app.exception_handler(Exception)
async def handle_unexpected_error(_: object, exc: Exception):
    return error_response(code="INTERNAL_SERVER_ERROR", message=str(exc), status_code=500)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("frontend/index.html")


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
