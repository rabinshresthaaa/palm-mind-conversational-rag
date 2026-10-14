
import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.models.booking import InterviewBooking
from app.services.booking_memory import (
    clear_booking_draft,
    get_booking_draft,
    save_booking_draft,
)
from app.services.llm import extract_booking_details

NEPAL_TZ = ZoneInfo("Asia/Kathmandu")
EMAIL_ADAPTER = TypeAdapter(EmailStr)

REQUIRED_FIELDS = ("name", "email", "date", "time")


def process_booking_message(
    session_id: str,
    message: str,
    db: Session,
) -> dict | None:
    draft = get_booking_draft(session_id)

    extracted = extract_booking_details(message, draft)

    if not extracted.get("booking_intent") and not draft:
        return None

    # Do not let missing or malformed LLM values overwrite good data.
    for field in REQUIRED_FIELDS:
        value = extracted.get(field)
        if isinstance(value, str) and value.strip():
            draft[field] = value.strip()

    draft["booking_intent"] = True
    save_booking_draft(session_id, draft)

    missing = [field for field in REQUIRED_FIELDS if not draft.get(field)]

    if missing:
        prompts = {
            "name": "What is your full name?",
            "email": "What email address should I use for the interview booking?",
            "date": "What date would you prefer for the interview?",
            "time": "What time would you prefer? Please include AM/PM or use 24-hour time.",
        }
        return {
            "answer": prompts[missing[0]],
            "booking_created": False,
            "booking_id": None,
        }

    name = draft["name"].strip()
    if len(name) < 2 or len(name) > 150:
        draft.pop("name", None)
        save_booking_draft(session_id, draft)
        return {
            "answer": "Please provide a valid full name between 2 and 150 characters.",
            "booking_created": False,
            "booking_id": None,
        }

    try:
        email = str(EMAIL_ADAPTER.validate_python(draft["email"])).lower()
    except ValidationError:
        draft.pop("email", None)
        save_booking_draft(session_id, draft)
        return {
            "answer": "That email address doesn't appear valid. Could you provide it again?",
            "booking_created": False,
            "booking_id": None,
        }

    try:
        interview_date = date.fromisoformat(draft["date"])
        parsed_time = time.fromisoformat(draft["time"])
        if parsed_time.tzinfo is not None:
            raise ValueError("Provide local Nepal time without a timezone suffix.")
        interview_at = datetime.combine(
            interview_date,
            parsed_time,
            tzinfo=NEPAL_TZ,
        )
    except ValueError:
        draft.pop("date", None)
        draft.pop("time", None)
        save_booking_draft(session_id, draft)
        return {
            "answer": "I couldn't interpret that date or time. Please provide the date as YYYY-MM-DD and time as HH:MM, or tell me the date and time again.",
            "booking_created": False,
            "booking_id": None,
        }

    if interview_at <= datetime.now(NEPAL_TZ):
        draft.pop("date", None)
        draft.pop("time", None)
        save_booking_draft(session_id, draft)
        return {
            "answer": "That date and time is in the past. What future date and time would you prefer?",
            "booking_created": False,
            "booking_id": None,
        }

    # Require a clear confirmation before writing to the database.
    if not draft.get("confirmed"):
        if re.search(r"\b(confirm|yes|book it|that is correct|that's correct)\b", message, re.I):
            draft["confirmed"] = True
            save_booking_draft(session_id, draft)
        else:
            save_booking_draft(session_id, draft)
            return {
                "answer": (
                    "Please confirm these interview details:\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Date and time: {interview_at.strftime('%Y-%m-%d %H:%M %Z')}\n\n"
                    "Reply 'confirm' to save this booking, or tell me what to change."
                ),
                "booking_created": False,
                "booking_id": None,
            }

    booking = InterviewBooking(
        name=name,
        email=email,
        interview_at=interview_at,
        status="confirmed",
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
    except Exception:
        db.rollback()
        raise

    booking_id = booking.id
    clear_booking_draft(session_id)

    return {
        "answer": (
            "Your interview booking has been saved successfully. "
            f"Your booking reference is {booking_id}."
        ),
        "booking_created": True,
        "booking_id": booking_id,
    }
