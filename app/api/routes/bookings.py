
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.booking import InterviewBooking
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
) -> BookingResponse:
    interview_at = booking_data.interview_at

    # Require a timezone so the interview time is unambiguous.
    if interview_at.tzinfo is None or interview_at.utcoffset() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "interview_at must include a timezone, "
                "for example 2026-11-10T14:00:00+05:45."
            ),
        )

    if interview_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The interview time must be in the future.",
        )

    booking = InterviewBooking(
        name=booking_data.name.strip(),
        email=str(booking_data.email).lower(),
        interview_at=interview_at,
        status="confirmed",
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return BookingResponse.model_validate(booking)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the interview booking.",
        ) from exc
