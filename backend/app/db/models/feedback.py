"""Feedback model for user vote/feedback submissions."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Feedback(Base):
    """Feedback model with idempotent key on (news_id, user, type)."""

    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("news_id", "submitted_by", "feedback_type", name="uq_feedback_news_user_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("news_articles.news_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    feedback_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Type: vote or feedback",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        comment="Status: pending, approved, rejected",
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Feedback(id={self.id}, news_id='{self.news_id}', "
            f"type='{self.feedback_type}', status='{self.status}')>"
        )
