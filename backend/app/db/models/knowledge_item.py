"""Knowledge item model for fraud RAG knowledge base."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False, default="case")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    conclusion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fraud_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    target_groups: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    signals: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    advice: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    submitted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<KnowledgeItem(id={self.id}, item_id='{self.item_id}', type='{self.item_type}', status='{self.status}')>"
