from pathlib import Path

import fitz  # PyMuPDF


class TextExtractionError(Exception):
    """Raised when a document cannot be extracted."""


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from a PDF or TXT file."""

    extension = Path(filename).suffix.lower()

    if not file_bytes:
        raise TextExtractionError("The uploaded file is empty.")

    if extension == ".txt":
        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise TextExtractionError(
                "The TXT file must use UTF-8 encoding."
            ) from exc

    elif extension == ".pdf":
        try:
            with fitz.open(
                stream=file_bytes,
                filetype="pdf",
            ) as pdf:
                text = "\n".join(
                    page.get_text() for page in pdf
                )
        except Exception as exc:
            raise TextExtractionError(
                "The PDF file could not be read."
            ) from exc

    else:
        raise TextExtractionError(
            "Unsupported file type. Upload a PDF or TXT file."
        )

    text = text.strip()

    if not text:
        raise TextExtractionError(
            "No readable text was found in the document."
        )

    return text