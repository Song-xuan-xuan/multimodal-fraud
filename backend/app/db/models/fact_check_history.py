"""Fact-check history model."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FactCheckHistory(Base):
    __tablename__ = "fact_check_history"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    save_type: Mapped[str] = mapped_column(String(50), default="all", nullable=False)
    checked_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<FactCheckHistory(id='{self.id}', verdict='{self.verdict}', checked_by='{self.checked_by}')>"
