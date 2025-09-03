from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.recording import Recording


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Common fields
    name: Mapped[Optional[str]] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Local auth
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Google OAuth fields
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    picture: Mapped[Optional[str]]
    email_verified: Mapped[Optional[bool]]

    # Optional extra field
    age: Mapped[Optional[int]]

    # One-to-many: a user can have many recordings
    recordings: Mapped[List["Recording"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
