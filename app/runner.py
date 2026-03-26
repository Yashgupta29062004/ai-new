from typing import List, Dict
import sys
from pathlib import Path

# Ensures internal imports work correctly if running as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import YOUTUBE_CHANNELS
from app.scrapers.youtube import YouTubeScraper
from app.scrapers.openai import OpenAI_Scraper
from app.scrapers.anthropic import AnthropicScraper
from app.databases.repositry import Repository  # Matches your folder 'databases' and file 'repositry.py'

def run_scraper(hours: int = 24) -> dict:
    # 1. Initialize Scrapers and Repo
    youtube_scraper = YouTubeScraper()
    openai_scraper = OpenAI_Scraper()      # Fixed: Match class name in openai.py
    anthropic_scraper = AnthropicScraper()
    repo = Repository()

    # --- YOUTUBE SECTION ---
    all_videos = []
    video_dicts = []
    for channel_id in YOUTUBE_CHANNELS:    # Fixed: Typo 'chaneel_id'
        # Fetches metadata via RSS
        videos = youtube_scraper.get_latest_videos(channel_id, hours=hours) # Fixed: Variable 'Channel_id'
        all_videos.extend(videos)
        
        for v in videos:
            video_dicts.append({
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript # This is usually None until processed
            })
    
    if video_dicts:
        # Fixed: Match method name in repositry.py (plural)
        repo.bulk_create_youtube_videos(video_dicts)

    # --- OPENAI SECTION ---
    # Fixed: Match method name in openai.py (singular 'get_article')
    openai_articles = openai_scraper.get_article(hours=hours) 
    
    if openai_articles:
        openai_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in openai_articles
        ]
        # Fixed: Match method name in repositry.py (plural)
        repo.bulk_create_openai_articles(openai_dicts)

    # --- ANTHROPIC SECTION ---
    # Fixed: Match method name in anthropic.py (plural 'get_articles')
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    
    if anthropic_articles:
        anthropic_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in anthropic_articles
        ]
        # Fixed: Match method name in repositry.py (plural)
        repo.bulk_create_anthropic_articles(anthropic_dicts)

    return {
        "youtube": all_videos,
        "openai": openai_articles,
        "anthropic": anthropic_articles
    }

if __name__ == "__main__":
    results = run_scraper(hours=24)
    print(f"--- Scraping Complete ---")
    print(f"YouTube videos found: {len(results['youtube'])}")
    print(f"OpenAI articles found: {len(results['openai'])}")
    print(f"Anthropic articles found: {len(results['anthropic'])}")