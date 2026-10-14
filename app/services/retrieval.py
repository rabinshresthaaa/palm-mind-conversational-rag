from app.services.embeddings import embed_texts
from app.services.vector_store import search_chunks


def retrieve_relevant_chunks(
    question: str,
    limit: int = 5,
) -> list[dict]:
    """Embed a question and retrieve matching document chunks."""
    vectors = embed_texts([question])

    if not vectors:
        return []

    return search_chunks(
        query_vector=vectors[0],
        limit=limit,
    )
