import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google import genai
from google.genai import types

from app.databases.repositry import Repository
from app.profiles.user_profile import USER_PROFILE

# gemini-2.5-flash: confirmed available quota on this API key
GEMINI_MODEL = "gemini-2.5-flash"

# Seconds to wait between API calls to avoid hitting rate limits
RATE_LIMIT_DELAY = 1.5

# Truncate content so we don't exceed context limits
MAX_CONTENT_CHARS = 8000


def _get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)


def _build_prompt(title: str, content: str, source: str) -> str:
    interests = "\n".join(f"  - {i}" for i in USER_PROFILE["interests"])
    truncated = content[:MAX_CONTENT_CHARS]
    return f"""You are an AI news curator for {USER_PROFILE['name']}, a {USER_PROFILE['title']}.

Their interests:
{interests}

Preferences: prefer practical, technical, and research-focused content. Avoid marketing hype.

---
Source: {source}
Title: {title}

Content:
{truncated}
---

Task:
1. Write a 3-sentence summary highlighting the practical significance of this article.
2. Score its relevance to this user on a scale of 1.0 to 10.0 (10 = must-read, 1 = irrelevant).

Respond ONLY with valid JSON — no markdown, no explanation:
{{"summary": "...", "score": 8.5}}"""


def _summarize(client: genai.Client, title: str, content: str, source: str) -> Optional[dict]:
    """Call Gemini with exponential backoff on 429 rate-limit errors."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=_build_prompt(title, content, source),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            time.sleep(RATE_LIMIT_DELAY)
            return json.loads(response.text)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait = RATE_LIMIT_DELAY * (2 ** attempt)  # 1.5s, 3s, 6s
                print(f"  Rate limited. Waiting {wait:.1f}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
            else:
                print(f"  Gemini error: {e}")
                time.sleep(RATE_LIMIT_DELAY)
                return None
    print(f"  Failed after {max_retries} retries.")
    return None


def process_digests(hours: int = 24) -> dict:
    """
    Main entry point called by daily_runner.py.
    Only processes articles scraped within the last `hours` hours.
    """
    client = _get_gemini_client()
    repo = Repository()

    processed = 0
    failed = 0

    # ── Anthropic articles ──────────────────────────────────────────────────
    anthropic_articles = repo.get_undigested_anthropic_articles(hours=hours)
    print(f" Found {len(anthropic_articles)} undigested Anthropic articles (last {hours}h).")

    for article in anthropic_articles:
        content = article.markdown or article.description or ""
        if not content.strip():
            failed += 1
            continue
        print(f"  Summarizing: {article.title[:60]}...")
        result = _summarize(client, article.title, content, "Anthropic")
        if result:
            repo.create_digest({
                "article_type": "anthropic",
                "article_id": article.guid,
                "url": article.url,
                "title": article.title,
                "summary": result["summary"],
                "score": result.get("score"),
            })
            processed += 1
        else:
            failed += 1

    # ── OpenAI articles ─────────────────────────────────────────────────────
    openai_articles = repo.get_undigested_openai_articles(hours=hours)
    print(f" Found {len(openai_articles)} undigested OpenAI articles (last {hours}h).")

    for article in openai_articles:
        content = article.description or ""
        if not content.strip():
            failed += 1
            continue
        print(f"  Summarizing: {article.title[:60]}...")
        result = _summarize(client, article.title, content, "OpenAI")
        if result:
            repo.create_digest({
                "article_type": "openai",
                "article_id": article.guid,
                "url": article.url,
                "title": article.title,
                "summary": result["summary"],
                "score": result.get("score"),
            })
            processed += 1
        else:
            failed += 1

    # ── YouTube videos ──────────────────────────────────────────────────────
    youtube_videos = repo.get_undigested_youtube_videos(hours=hours)
    print(f" Found {len(youtube_videos)} undigested YouTube videos (last {hours}h).")

    for video in youtube_videos:
        content = video.transcript or ""
        if not content.strip():
            failed += 1
            continue
        print(f"  Summarizing: {video.title[:60]}...")
        result = _summarize(client, video.title, content, "YouTube")
        if result:
            repo.create_digest({
                "article_type": "youtube",
                "article_id": video.video_id,
                "url": video.url,
                "title": video.title,
                "summary": result["summary"],
                "score": result.get("score"),
            })
            processed += 1
        else:
            failed += 1

    total = processed + failed
    print(f"\n Digest processing complete: {processed}/{total} succeeded.")
    return {"total": total, "processed": processed, "failed": failed}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(" Starting digest generation with Gemini...")
    stats = process_digests()
    print(f"\n--- Digest Stats ---")
    print(f"Total:     {stats['total']}")
    print(f"Processed: {stats['processed']}")
    print(f"Failed:    {stats['failed']}")
