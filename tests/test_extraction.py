import fitz
import pytest

from app.services.extraction import (
    TextExtractionError,
    extract_text,
)


def test_extract_txt() -> None:
    result = extract_text(
        b"Hello from Palm Mind AI",
        "sample.txt",
    )

    assert result == "Hello from Palm Mind AI"


def test_reject_unsupported_file() -> None:
    with pytest.raises(TextExtractionError):
        extract_text(b"some data", "sample.docx")


def test_reject_empty_file() -> None:
    with pytest.raises(TextExtractionError):
        extract_text(b"", "empty.txt")


def test_extract_pdf() -> None:
    pdf_bytes = b""

    with fitz.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72, 72), "Palm Mind AI test")
        pdf_bytes = pdf.tobytes()

    result = extract_text(pdf_bytes, "sample.pdf")

    assert "Palm Mind AI test" in result