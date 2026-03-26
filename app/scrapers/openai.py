from datetime import datetime, timedelta, timezone
from typing import List, Optional
import feedparser
from pydantic import BaseModel

class OpenAI_Article(BaseModel):
    title: str
    description: str
    url: str
    guid: str
    published_at: datetime
    category: Optional[str] = None

class OpenAI_Scraper:
    def __init__(self):
        # OpenAI sometimes uses different RSS endpoints; this is the most common one
        self.rss_url = "https://openai.com/news/rss.xml"
        
    def get_article(self, hours: int = 24) -> List[OpenAI_Article]:
        feed = feedparser.parse(self.rss_url)
        
        # DEBUG: Check if feed actually loaded
        if not feed.entries:
            print("No entries found in feed. Check the URL or Network.")
            return []
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        articles = []

        for entry in feed.entries:
            published_parsed = getattr(entry, "published_parsed", None)
            if not published_parsed:
                continue
            
            # Convert to UTC datetime
            published_time = datetime(*published_parsed[:6], tzinfo=timezone.utc)
            
            if published_time >= cutoff_time:
                # Safer Category Extraction
                category = None
                if 'tags' in entry and entry.tags:
                    category = entry.tags[0].get('term')
                elif 'category' in entry:
                    category = entry.category

                articles.append(OpenAI_Article(
                    title=entry.get("title", "No Title"),
                    description=entry.get("summary", entry.get("description", "")), # OpenAI uses 'summary' often
                    url=entry.get("link", ""),
                    guid=entry.get("id", entry.get("link", "")),
                    published_at=published_time,
                    category=category
                ))
        
        return articles

if __name__ == "__main__":
    scraper = OpenAI_Scraper()
    # Use a larger window (e.g., 500 hours) to test if it's a timing issue
    found_articles = scraper.get_article(hours=500)
    print(f"Total articles found: {len(found_articles)}")
    for a in found_articles[:3]: # Print first 3 to verify
        print(f"- {a.title} ({a.published_at})")