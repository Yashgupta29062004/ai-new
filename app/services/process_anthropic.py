from typing import Optional
import sys
from pathlib import Path

# Ensures the 'app' package is discoverable from this subfolder
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.anthropic import AnthropicScraper
from app.databases.repositry import Repository

def process_anthropic_markdown(limit: Optional[int] = None) -> dict:
    scraper = AnthropicScraper()
    repo = Repository()
    
    # 1. Fetch articles where markdown is NULL
    articles = repo.get_anthropic_articles_without_markdown(limit=limit)
    
    processed = 0
    failed = 0
    total = len(articles)
    
    if not articles:
        print(" No Anthropic articles found that need markdown extraction.")
        return {"total": 0, "processed": 0, "failed": 0}

    print(f" Found {total} Anthropic articles to process...")

    for article in articles:
        print(f"Scraping content for: {article.title[:50]}...")
        try:
            # 2. Process each URL using the scraper's markdown converter
            # Note: Ensure your AnthropicScraper has a 'url_to_markdown' method
            markdown_content = scraper.url_to_markdown(article.url)
            
            if markdown_content:
                # 3. Update the database with extracted markdown
                repo.update_anthropic_article_markdown(article.guid, markdown_content)
                print(f"Success: Saved markdown for {article.guid[:30]}...")
                processed += 1
            else:
                print(f"⚠️ Warning: No content extracted for {article.url}")
                failed += 1
                
        except Exception as e:
            failed += 1
            print(f" Error processing {article.url}: {e}")
    
    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }

if __name__ == "__main__":
    print(" Starting Anthropic Markdown Extraction...")
    stats = process_anthropic_markdown()
    
    print(f"\n--- Extraction Stats ---")
    print(f"Total articles found: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Failed/Empty results :   {stats['failed']}")
    print(f"--------")