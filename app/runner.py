from typing import List
from .config import YOUTUBE_CHANNELS
from .scrapers.youtube import ChannelVideo , YouTubeScraper
from .scrapers.openai import OpenAI_Article,OpenAI_Scraper
from .scrapers.anthropic import AnthropicArticle,AnthropicScraper
from .repository import Repository

def run_scraper(hours:int=24)->dict:
    youtube_scraper=YouTubeScraper()
    openai_scraper=OpenAi_Scraper()
    anthropic_scraper=AnthropicScraper()
    repo=Repository()

    youtube_videos=[]
    video_dicts=[]
    for chaneel_id in YOUTUBE_CHANNELS:
        videos=youtube_scraper.get_latest_videos(Channel_id,hours=hours)
        youtube_videos.extend(videos)
        video_dict.extend([
            {
            "video_id":v.video_id,
            "title":v.title,
            "url":v.url,
           
            "published_at":v.published_at,
            "transcript":v.transcript

        }
        for v in videos
    ])
    openai_aricle=openai_scraper.get_articles(hours=hours)
    anthropic_article=anthropic_scraper.get_article(hours=hours)

    if video_dicts:
        repo.bulk_create_youtube_video(video_dicts)
    
    if openai_articles:
        article_dict=[
            {
                "guid":a.guid,
                "title":a.title,
                "url":a.url,

                "published_at":a.published_at,
                "description":a.description,

                "category":a.category

            }
            for a in openai_articles
        ]
        repo.bulk_create_openai_article(article_dict)
    if anthropic_articles:
        article_dict=[
            {
                "guid":a.guid,
                "title":a.title,
                "url":a.url,

                "published_at":a.published_at,
                "description":a.description,

                "category":a.category

            }
            for a in anthropic_articles
        ]
        repo.bulk_create_anthropic_article(article_dict)
    return{
        "youtube":youtube_videos,
        "openai":openai_article,
        "anthropic":anthropic_article
    }

if __name__=="__main__":
    results=run_scraper(hours=24)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")

    
    