from uuid import uuid4

from qdrant_client import QdrantClient, models

from app.core.config import settings


COLLECTION_NAME = "palm_mind_documents"
VECTOR_SIZE = 384


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection() -> None:
    client = get_qdrant_client()

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def store_chunks(
    document_id: int,
    filename: str,
    chunks: list[str],
    vectors: list[list[float]],
) -> None:
    if len(chunks) != len(vectors):
        raise ValueError("Each chunk must have one embedding vector.")

    if not chunks:
        return

    client = get_qdrant_client()
    ensure_collection()

    points = [
        models.PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
                "text": chunk,
            },
        )
        for index, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )

def search_chunks(
    query_vector: list[float],
    limit: int = 5,
) -> list[dict]:
    """Retrieve the most relevant document chunks from Qdrant."""
    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20.")

    client = get_qdrant_client()

    if not client.collection_exists(COLLECTION_NAME):
        return []

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    results: list[dict] = []

    for point in response.points:
        payload = point.payload or {}

        results.append(
            {
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "chunk_index": payload.get("chunk_index"),
                "text": payload.get("text", ""),
                "score": point.score,
            }
        )

    return results
