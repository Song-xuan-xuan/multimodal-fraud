"""Evidence model for news verification."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Evidence(Base):
    """Evidence model for crowdsourced news verification."""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("news_articles.news_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    submitted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        comment="Status: pending, approved, rejected"
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Evidence(id={self.id}, news_id='{self.news_id}', status='{self.status}')>"
