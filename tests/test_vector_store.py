from app.services.vector_store import (
    COLLECTION_NAME,
    VECTOR_SIZE,
    ensure_collection,
    get_qdrant_client,
)


def test_qdrant_collection_exists() -> None:
    ensure_collection()

    client = get_qdrant_client()

    assert client.collection_exists(COLLECTION_NAME)

    info = client.get_collection(COLLECTION_NAME)
    assert info.config.params.vectors.size == VECTOR_SIZE