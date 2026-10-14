import json

import redis

from app.core.config import settings


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def get_chat_history(
    session_id: str,
    limit: int = 10,
) -> list[dict[str, str]]:
    client = get_redis_client()
    key = f"chat:{session_id}:history"

    messages = client.lrange(key, -limit, -1)

    return [json.loads(message) for message in messages]


def save_chat_message(
    session_id: str,
    role: str,
    content: str,
) -> None:
    client = get_redis_client()
    key = f"chat:{session_id}:history"

    message = json.dumps({
        "role": role,
        "content": content,
    })

    client.rpush(key, message)
    client.ltrim(key, -10, -1)
    client.expire(key, 86400)