from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentUploadResponse
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts
from app.services.extraction import TextExtractionError, extract_text
from app.services.vector_store import store_chunks


router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=201,
)
def upload_document(
    file: UploadFile = File(...),
    strategy: str = Form("fixed"),
    chunk_size: int = Form(1000),
    overlap: int = Form(200),
    db: Session = Depends(get_db),
) -> Document:
    """Upload, extract, chunk, embed, and index a document."""

    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    if strategy not in {"fixed", "sentence"}:
        raise HTTPException(
            status_code=400,
            detail="strategy must be 'fixed' or 'sentence'.",
        )

    if chunk_size < 1 or chunk_size > 10000:
        raise HTTPException(
            status_code=400,
            detail="chunk_size must be between 1 and 10000.",
        )

    if overlap < 0 or overlap >= chunk_size:
        raise HTTPException(
            status_code=400,
            detail="overlap must be >= 0 and less than chunk_size.",
        )

    file_bytes = file.file.read(MAX_FILE_SIZE + 1)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB upload limit.",
        )

    document = Document(
        filename=filename,
        file_type=extension.lstrip("."),
        status="processing",
        chunk_count=0,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        text = extract_text(file_bytes, filename)

        chunks = chunk_text(
            text,
            strategy=strategy,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:
            raise TextExtractionError(
                "No usable text chunks were produced."
            )

        vectors = embed_texts(chunks)

        store_chunks(
            document_id=document.id,
            filename=filename,
            chunks=chunks,
            vectors=vectors,
        )

        document.status = "processed"
        document.chunk_count = len(chunks)
        db.commit()
        db.refresh(document)

        return document

    except TextExtractionError as exc:
        db.rollback()
        document = db.get(Document, document.id)
        if document is not None:
            document.status = "failed"
            db.commit()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        document = db.get(Document, document.id)
        if document is not None:
            document.status = "failed"
            db.commit()

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check the application logs.",
        ) from exc