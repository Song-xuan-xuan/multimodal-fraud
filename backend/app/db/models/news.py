"""News article model."""
from typing import Optional

from sqlalchemy import Boolean, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NewsArticle(Base):
    """News article model with credibility analysis and verification data."""

    __tablename__ = "news_articles"

    # Primary identification
    news_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Basic information
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    pic_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Metadata
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashtag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    conclusion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamd as strings to maintain compatibility with original system)
    publish_time: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    check_time: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Credibility flag
    iscredit: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Credibility scoring
    credibility_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    credibility_dimensions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Stores dimension_scores: source, content, logic, propagation, AI, content1, content2"
    )

    # Verification status
    verification_progress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verified: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Propagation data
    propagation_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Stores timeline (timestamp, platform, shares, geo_distribution) and user_profile (age_dist, device_ratio)"
    )

    # Relations data
    relations_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Stores related_rumors and knowledge_nodes"
    )

    def __repr__(self) -> str:
        return f"<NewsArticle(news_id='{self.news_id}', title='{self.title[:50] if self.title else None}...')>"
