from fastapi import FastAPI

from app.api.routes.chat import router as chat_router

from app.api.routes.bookings import router as bookings_router

from app.api.routes.documents import router as documents_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "Document ingestion, retrieval, chat memory, "
        "and interview booking."
    ),
    version="0.1.0",
)

app.include_router(
    documents_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    chat_router, 
    prefix=settings.api_v1_prefix
)

app.include_router(
    bookings_router,
    prefix=settings.api_v1_prefix,
)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Palm Mind RAG backend is running!"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}