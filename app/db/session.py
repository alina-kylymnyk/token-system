from typing import Generator
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get DB session
    Used in FastAPI endpoints
    """
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
        