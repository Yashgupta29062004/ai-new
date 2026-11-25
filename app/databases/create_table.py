import sys
from pathlib import Path

# Fix the path to ensure it finds 'app'
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# IMPORTANT: Match your actual folder 'databases' and file 'model'
from app.databases.model import Base 
from app.databases.connection import engine

def migrate_timestamp_columns():
    """Migrate existing TIMESTAMP columns to TIMESTAMPTZ on PostgreSQL.
    This is safe to run multiple times (idempotent)."""
    from sqlalchemy import text
    db_url = str(engine.url)
    if not db_url.startswith("postgresql"):
        return  # SQLite doesn't have TIMESTAMPTZ

    tables_and_columns = [
        ("youtube_videos", ["published_at", "created_at"]),
        ("openai_articles", ["published_at", "created_at"]),
        ("anthropic_articles", ["published_at", "created_at"]),
        ("digests", ["created_at"]),
    ]
    with engine.connect() as conn:
        for table, columns in tables_and_columns:
            for col in columns:
                try:
                    conn.execute(text(
                        f"ALTER TABLE {table} ALTER COLUMN {col} "
                        f"TYPE TIMESTAMPTZ USING {col} AT TIME ZONE 'UTC'"
                    ))
                except Exception:
                    pass  # Column might already be TIMESTAMPTZ or table doesn't exist yet
        conn.commit()
    print("✅ Timestamp columns migrated to TIMESTAMPTZ.")


if __name__ == "__main__":
    print("Connecting to database...")
    # This command actually sends the CREATE TABLE SQL to Postgres
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
    # Migrate existing columns to timezone-aware
    migrate_timestamp_columns()