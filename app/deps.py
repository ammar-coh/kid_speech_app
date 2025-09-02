from typing import Generator
from app.db import SessionLocal

# Dependency for getting a DB session per request
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db           # Provide the session to the request
        db.commit()        # Commit if everything goes fine
    except:
        db.rollback()      # Rollback if an error occurs
        raise
    finally:
        db.close()         # Always close the session
