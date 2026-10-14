import pytest

from app.services.chunking import (
    chunk_text,
    fixed_size_chunking,
    sentence_aware_chunking,
)


def test_fixed_chunking_respects_overlap() -> None:
    text = "A" * 2500

    chunks = fixed_size_chunking(
        text,
        chunk_size=1000,
        overlap=200,
    )

    assert len(chunks) == 3
    assert chunks[0][-200:] == chunks[1][:200]


def test_fixed_chunking_empty_text() -> None:
    assert fixed_size_chunking("   ") == []


def test_sentence_chunking_keeps_short_sentences() -> None:
    chunks = sentence_aware_chunking(
        "First sentence. Second sentence. Third sentence.",
        chunk_size=35,
    )

    assert len(chunks) == 2
    assert "First sentence." in chunks[0]


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(ValueError):
        fixed_size_chunking(
            "some text",
            chunk_size=100,
            overlap=100,
        )


def test_strategy_selection() -> None:
    chunks = chunk_text(
        "First sentence. Second sentence.",
        strategy="sentence",
    )

    assert len(chunks) == 1


def test_unknown_strategy_is_rejected() -> None:
    with pytest.raises(ValueError):
        chunk_text("Hello", strategy="unknown")
