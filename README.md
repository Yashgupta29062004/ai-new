# 🤖 AI News Aggregator

A daily pipeline that scrapes AI news from **YouTube**, **OpenAI**, and **Anthropic**, summarizes and ranks each article using **Gemini**, then delivers a beautiful digest straight to your **Gmail** inbox every day.

---

## Pipeline Overview

```
[1] Scrape        → YouTube (transcripts) + OpenAI RSS + Anthropic RSS
[2] Enrich        → Anthropic articles → Markdown (Docling)
                    YouTube videos   → Transcripts (YouTube Transcript API)
[3] Digest        → Gemini summarizes each item + assigns a relevance score (1–10)
[4] Email         → Top-ranked digest sent as a styled HTML email via Gmail SMTP
```

---

## Quick Start

### 1. Prerequisites
- Python 3.12+
- PostgreSQL (or Docker)
- A [Gemini API Key](https://aistudio.google.com/app/apikey) (free tier available)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords)

### 2. Clone & install dependencies

```bash
# Install uv (fast Python package manager)
curl -Ls https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync
```

### 3. Start the database

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 4. Configure environment variables

Copy and fill in your values:

```bash
cp .env .env.local   # optional: keep a backup
```

Edit `.env`:

| Variable | Description |
|---|---|
| `POSTGRES_*` | Database connection settings |
| `GEMINI_API_KEY` | Your Google AI Studio API key |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password (16 chars, NOT your login password) |
| `DIGEST_EMAIL_TO` | Where to send the daily digest |

### 5. Create database tables

```bash
uv run python app/databases/create_table.py
```

### 6. Run the full pipeline

```bash
uv run python -m app.daily_runner
```

---

## Running Individual Steps

```bash
# Step 1: Scrape all sources
uv run python -m app.runner

# Step 2a: Extract Anthropic article markdown
uv run python app/services/process_anthropic.py

# Step 2b: Fetch YouTube transcripts
uv run python app/services/process_youtube.py

# Step 3: Generate digests with Gemini
uv run python app/services/process_digest.py

# Step 4: Send the email
uv run python app/services/process_email.py
```

---

## Docker Deployment

```bash
# Build
docker build -t ai-news-aggregator .

# Run (pass your .env file)
docker run --env-file .env ai-news-aggregator
```

---

## Project Structure

```
app/
├── config.py               # YouTube channel IDs to monitor
├── runner.py               # Scraping orchestrator (Step 1)
├── daily_runner.py         # Full pipeline runner (Steps 1–4)
├── scrapers/
│   ├── anthropic.py        # Anthropic RSS + Docling markdown
│   ├── openai.py           # OpenAI RSS feed parser
│   └── youtube.py          # YouTube RSS + transcript fetcher
├── services/
│   ├── process_anthropic.py  # Enrich Anthropic articles with markdown
│   ├── process_youtube.py    # Enrich YouTube videos with transcripts
│   ├── process_digest.py     # Gemini summarization + scoring
│   └── process_email.py      # Gmail digest email sender
├── databases/
│   ├── model.py            # SQLAlchemy ORM models
│   ├── connection.py       # DB session factory
│   ├── repositry.py        # All DB read/write operations
│   └── create_table.py     # One-time table creation script
└── profiles/
    └── user_profile.py     # Your interests (used to personalize scores)
```

---

## Scheduling (Daily Cron)

To run automatically every day at 7 AM:

```bash
# Open crontab
crontab -e

# Add this line (adjust the path)
0 7 * * * cd /path/to/ai-new && uv run python -m app.daily_runner >> logs/cron.log 2>&1
```

---

## Adding More YouTube Channels

Edit `app/config.py`:

```python
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
    "UCbmNph6atAoGfqLoCL_duAg",  # Andrej Karpathy
    # Add more channel IDs here
]
```