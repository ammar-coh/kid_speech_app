from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.evaluation import Evaluation


class Recording(Base):
    __tablename__ = "recordings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    transcription: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Many-to-one: many recordings → one user
    user: Mapped["User"] = relationship(back_populates="recordings")

    # One-to-one: one recording → one evaluation
    evaluation: Mapped[Optional["Evaluation"]] = relationship(
        back_populates="recording", uselist=False, cascade="all, delete-orphan"
    )
