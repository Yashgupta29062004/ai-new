from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
# Ensure this matches your file name: model.py
from .model import YoutubeVideos, OpenAIArticle, AnthropicArticle, Digest
from .connection import get_session

class Repository:
    def __init__(self, session: Optional[Session] = None):
        # Using a context manager for the session is safer to ensure data is saved
        self.session = session or get_session()

    # --- BULK CREATE METHODS (MOST IMPORTANT) ---

    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []
        print(f" Repo: Processing {len(articles)} OpenAI articles...")
        
        for a in articles:
            # Check for existing GUID to prevent duplicates
            existing = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        
        if new_articles:
            try:
                self.session.add_all(new_articles)
                self.session.commit()
                print(f" Success: {len(new_articles)} OpenAI articles saved to DB.")
            except Exception as e:
                self.session.rollback()
                print(f" Database Error: {e}")
                return 0
        else:
            print(" No new OpenAI articles found (all were duplicates).")
            
        return len(new_articles)

    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        new_articles = []
        print(f" Repo: Processing {len(articles)} Anthropic articles...")
        
        for a in articles:
            existing = self.session.query(AnthropicArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(AnthropicArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))
        
        if new_articles:
            try:
                self.session.add_all(new_articles)
                self.session.commit()
                print(f" Success: {len(new_articles)} Anthropic articles saved.")
            except Exception as e:
                self.session.rollback()
                print(f"Error: {e}")
                return 0
        return len(new_articles)

    def bulk_create_youtube_videos(self, videos: List[dict]) -> int:
        new_videos = []
        for v in videos:
            existing = self.session.query(YoutubeVideos).filter_by(video_id=v["video_id"]).first()
            if not existing:
                new_videos.append(YoutubeVideos(
                    video_id=v["video_id"],
                    title=v["title"],
                    url=v["url"],
                    channel_id=v.get("channel_id", ""),
                    published_at=v["published_at"],
                    description=v.get("description", ""),
                    transcript=v.get("transcript")
                ))
        if new_videos:
            try:
                self.session.add_all(new_videos)
                self.session.commit()
                print(f" Success: {len(new_videos)} YouTube videos saved.")
            except Exception as e:
                self.session.rollback()
                print(f" Error: {e}")
        return len(new_videos)

    # --- UPDATE METHODS ---

    def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(AnthropicArticle).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            self.session.commit()
            return True
        return False

    def update_youtube_video_transcript(self, video_id: str, transcript: str) -> bool:
        video = self.session.query(YoutubeVideos).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            self.session.commit()
            return True
        return False

    # --- HELPER METHODS FOR PIPELINE ---

    def get_anthropic_articles_without_markdown(self, limit: Optional[int] = None) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(AnthropicArticle.markdown.is_(None))
        if limit: query = query.limit(limit)
        return query.all()

    def get_youtube_videos_without_transcript(self, limit: Optional[int] = None) -> List[YoutubeVideos]:
        query = self.session.query(YoutubeVideos).filter(YoutubeVideos.transcript.is_(None))
        if limit: query = query.limit(limit)
        return query.all()

    def __del__(self):
        """Ensure the session is closed when the repository is destroyed"""
        try:
            self.session.close()
        except:
            pass