from app.db.session import Base, engine
from app.models.document import Document
from app.models.booking import InterviewBooking

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()