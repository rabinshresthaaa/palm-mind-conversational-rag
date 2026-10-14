from app.services.embeddings import embed_texts, embedding_dimension


def test_embedding_dimension() -> None:
    assert embedding_dimension() == 384


def test_embed_texts() -> None:
    vectors = embed_texts([
        "FastAPI builds APIs.",
        "Qdrant stores vector embeddings.",
    ])

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert all(isinstance(value, float) for value in vectors[0])


def test_empty_input() -> None:
    assert embed_texts([]) == []