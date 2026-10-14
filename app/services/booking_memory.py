
import json

from app.services.chat_memory import get_redis_client


def get_booking_draft(session_id: str) -> dict:
    client = get_redis_client()
    raw = client.get(f"chat:{session_id}:booking_draft")

    if not raw:
        return {}

    return json.loads(raw)


def save_booking_draft(session_id: str, draft: dict) -> None:
    client = get_redis_client()
    client.set(
        f"chat:{session_id}:booking_draft",
        json.dumps(draft),
        ex=86400,
    )


def clear_booking_draft(session_id: str) -> None:
    client = get_redis_client()
    client.delete(f"chat:{session_id}:booking_draft")
