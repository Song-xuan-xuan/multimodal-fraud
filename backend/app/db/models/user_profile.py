"""User profile model for personalized anti-fraud protection."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    age_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    concern_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    guardian_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guardian_relation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    guardian_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    guardian_notify_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id})>"
