from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:  # Only for IDE / static type checkers
    from app.models.recording import Recording


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    age: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # One-to-many: a user can have many recordings
    recordings: Mapped[List["Recording"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
