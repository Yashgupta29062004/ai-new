import os

# ── Time window ────────────────────────────────────────────────────────────────
# How far back the pipeline looks for new content.
# 48 hours ensures we catch articles even if companies don't publish daily.
# All steps (scraping, enrichment, digest, email) respect this value.
PIPELINE_HOURS = int(os.getenv("PIPELINE_HOURS", "48"))

# ── YouTube channels to monitor ────────────────────────────────────────────────
YOUTUBE_CHANNELS = [
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
]

# ── Digest settings ────────────────────────────────────────────────────────────
# How many top articles to include in the daily email
TOP_N_DIGEST = int(os.getenv("TOP_N_DIGEST", "10"))