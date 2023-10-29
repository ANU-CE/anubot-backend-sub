from app.db.session import engine, SessionLocal
from typing import Generator

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()