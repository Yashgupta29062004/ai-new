from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, DateTime, Text, Float
from sqlalchemy.orm import declarative_base


def _utcnow():
    """Return timezone-aware UTC datetime. Fixes naive vs aware comparison bug."""
    return datetime.now(timezone.utc)


Base = declarative_base()


class YoutubeVideos(Base):
    __tablename__ = "youtube_videos"
    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class OpenAIArticle(Base):
    __tablename__ = "openai_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class AnthropicArticle(Base):
    __tablename__ = "anthropic_articles"

    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=False)
    category = Column(String, nullable=True)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class Digest(Base):
    __tablename__ = "digests"
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)   # 'anthropic', 'openai', 'youtube'
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    score = Column(Float, nullable=True)             # Relevance score 1-10 from Gemini
    created_at = Column(DateTime(timezone=True), default=_utcnow)




