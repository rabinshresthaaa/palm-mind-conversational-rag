from app.services.llm import generate_rag_answer


def test_generate_rag_answer() -> None:
    answer = generate_rag_answer(
        question="What does Qdrant store?",
        context=(
            "Qdrant stores vectors for semantic search. "
            "Each vector can have a payload containing text "
            "and document metadata."
        ),
    )

    assert isinstance(answer, str)
    assert len(answer) > 0