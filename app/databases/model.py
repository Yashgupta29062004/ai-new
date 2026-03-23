from datetime import datetime
from typing import Optional
from sqlalchemy import Column,String,DateTime,Text
from sqlalcemy.orm import declarative_base

Base=declarative_base()

class YoutubeVideos(Base):
    __tablename__="youtube_videos"
    video_id=Column(String,primary_key=True)
    title=Column(String,nullable=False)
    url=Column(String,nullable=False)
    channel_id=Column(String,nullable=False)
    published_at=Column(DateTime,nullable=False)
    decription=Column(Text)
    transcript=Column(Text,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)


class OpenAIArticle(Base):
    __tablename__ = "openai_articles"
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnthropicArticle(Base):
    __tablename__ = "anthropic_articles"
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Digest(Base):
    __tablename__="digests"
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)




