# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (layer-cache friendly)
COPY pyproject.toml uv.lock ./

# Install all dependencies into a virtual environment
RUN uv sync --frozen --no-dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Add the venv to PATH so Python finds installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source
COPY . .

# Auto-create tables (idempotent), then run the full daily pipeline
CMD ["sh", "-c", "python app/databases/create_table.py && python -m app.daily_runner"]
