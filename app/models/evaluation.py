from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.recording import Recording


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recording_id: Mapped[int] = mapped_column(
        ForeignKey("recordings.id"), nullable=False, unique=True
    )
    score: Mapped[float]
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # One-to-one: one evaluation → one recording
    recording: Mapped["Recording"] = relationship(back_populates="evaluation")
