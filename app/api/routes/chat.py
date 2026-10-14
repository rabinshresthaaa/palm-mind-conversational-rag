from fastapi import APIRouter, HTTPException, Depends
from redis.exceptions import RedisError
from groq import Groq

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.booking_flow import process_booking_message

from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.chat_memory import (
    get_chat_history,
    save_chat_message,
)
from app.services.llm import generate_rag_answer
from app.services.retrieval import retrieve_relevant_chunks

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:

        booking_result = process_booking_message(
            session_id=request.session_id,
            message=request.message,
            db=db,
        )

        if booking_result is not None:
            save_chat_message(
                request.session_id,
                "user",
                request.message,
            )
            save_chat_message(
                request.session_id,
                "assistant",
                booking_result["answer"],
            )

            return ChatResponse(
                session_id=request.session_id,
                answer=booking_result["answer"],
                sources=[],
                booking_created=booking_result["booking_created"],
                booking_id=booking_result["booking_id"],
            )
        # 1. Load recent messages for this conversation.
        history = get_chat_history(request.session_id)

        # 2. Search Qdrant for relevant document chunks.
        results = retrieve_relevant_chunks(request.message, limit=5)

        sources: list[SourceChunk] = []
        context_parts: list[str] = []

        for result in results:
            payload = result.get("payload", result)
            if not isinstance(payload, dict):
                continue

            text = payload.get("text", "")
            if not text:
                continue

            score = float(result.get("score", 0.0))

            sources.append(
                SourceChunk(
                    document_id=payload.get("document_id"),
                    filename=payload.get("filename"),
                    chunk_index=payload.get("chunk_index"),
                    text=text,
                    score=score,
                )
            )

            context_parts.append(
                f"Source: {payload.get('filename', 'Unknown document')}\n"
                f"Content: {text}"
            )

        # 3. Generate an answer using the context and chat history.
        context = "\n\n".join(context_parts)
        answer = generate_rag_answer(
            question=request.message,
            context=context,
            history=history,
        )

        # 4. Save the current exchange for the next turn.
        save_chat_message(
            request.session_id,
            "user",
            request.message,
        )
        save_chat_message(
            request.session_id,
            "assistant",
            answer,
        )

        # 5. Return the answer and supporting sources.
        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            sources=sources,
        )

    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Chat memory is temporarily unavailable.",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question.",
        ) from exc