from app.services.retrieval import retrieve_relevant_chunks


def test_retrieve_uploaded_document() -> None:
    results = retrieve_relevant_chunks(
        "How does Qdrant store information?",
        limit=5,
    )

    assert results, "Upload a sample document before running this test."
    assert any(result["text"] for result in results)
    assert all("score" in result for result in results)
