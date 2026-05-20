from datetime import datetime, timedelta, timezone
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from .model import YoutubeVideos, OpenAIArticle, AnthropicArticle, Digest
from .connection import get_session


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()

    # --- BULK CREATE METHODS ---

    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []
        print(f" Repo: Processing {len(articles)} OpenAI articles...")
        for a in articles:
            existing = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not existing:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category"),
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
                    category=a.get("category"),
                ))
        if new_articles:
            try:
                self.session.add_all(new_articles)
                self.session.commit()
                print(f" Success: {len(new_articles)} Anthropic articles saved.")
            except Exception as e:
                self.session.rollback()
                print(f" Error: {e}")
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
                    transcript=v.get("transcript"),
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

    # --- ENRICHMENT HELPERS ---

    def get_anthropic_articles_without_markdown(self, limit: Optional[int] = None) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(AnthropicArticle.markdown.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_youtube_videos_without_transcript(self, limit: Optional[int] = None) -> List[YoutubeVideos]:
        query = self.session.query(YoutubeVideos).filter(YoutubeVideos.transcript.is_(None))
        if limit:
            query = query.limit(limit)
        return query.all()

    # --- DIGEST METHODS ---

    def get_undigested_anthropic_articles(self, hours: int = 24) -> List[AnthropicArticle]:
        """Anthropic articles with markdown that were scraped within the last N hours and haven't been summarized."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        digested_ids = (
            self.session.query(Digest.article_id)
            .filter(Digest.article_type == "anthropic")
            .subquery()
        )
        return (
            self.session.query(AnthropicArticle)
            .filter(
                AnthropicArticle.guid.notin_(digested_ids),
                AnthropicArticle.markdown.isnot(None),
                AnthropicArticle.created_at >= cutoff,
            )
            .all()
        )

    def get_undigested_openai_articles(self, hours: int = 24) -> List[OpenAIArticle]:
        """OpenAI articles scraped within the last N hours that haven't been summarized yet."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        digested_ids = (
            self.session.query(Digest.article_id)
            .filter(Digest.article_type == "openai")
            .subquery()
        )
        return (
            self.session.query(OpenAIArticle)
            .filter(
                OpenAIArticle.guid.notin_(digested_ids),
                OpenAIArticle.created_at >= cutoff,
            )
            .all()
        )

    def get_undigested_youtube_videos(self, hours: int = 24) -> List[YoutubeVideos]:
        """YouTube videos with transcripts scraped within the last N hours that haven't been summarized."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        digested_ids = (
            self.session.query(Digest.article_id)
            .filter(Digest.article_type == "youtube")
            .subquery()
        )
        return (
            self.session.query(YoutubeVideos)
            .filter(
                YoutubeVideos.video_id.notin_(digested_ids),
                YoutubeVideos.transcript.isnot(None),
                YoutubeVideos.transcript != "__UNAVAILABLE__",
                YoutubeVideos.created_at >= cutoff,
            )
            .all()
        )

    def create_digest(self, digest_data: dict) -> bool:
        """Persist a single digest (summary + score) to the database."""
        try:
            digest = Digest(
                id=str(uuid.uuid4()),
                article_type=digest_data["article_type"],
                article_id=digest_data["article_id"],
                url=digest_data["url"],
                title=digest_data["title"],
                summary=digest_data["summary"],
                score=digest_data.get("score"),
            )
            self.session.add(digest)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f" Error saving digest: {e}")
            return False

    def get_recent_digests(self, hours: int = 24, top_n: int = 10) -> List[Digest]:
        """Fetch top-ranked digests from the last N hours, sorted by score descending."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return (
            self.session.query(Digest)
            .filter(Digest.created_at >= cutoff)
            .order_by(Digest.score.desc())
            .limit(top_n)
            .all()
        )

    def __del__(self):
        """Ensure the session is closed when the repository is destroyed."""
        try:
            self.session.close()
        except Exception:
            pass