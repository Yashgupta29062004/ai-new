import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from dotenv import load_dotenv

load_dotenv(override=False)  # Real env vars (GitHub Actions secrets) always win over .env

def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        db_url = db_url.strip().strip("'\"")
        # Remove channel_binding parameter which can cause issues with psycopg2 and Neon poolers
        db_url = db_url.replace("&channel_binding=require", "").replace("?channel_binding=require&", "?").replace("?channel_binding=require", "")
        return db_url
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Create the database engine with automatic fallback for SQLite
db_url = get_database_url()
try:
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False}, echo=False)
    else:
        engine = create_engine(db_url, connect_args={"connect_timeout": 15}, echo=False)
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"⚠️  Could not connect to PostgreSQL ({e}). Using local SQLite database (ai_news.db).")
    sqlite_url = "sqlite:///./ai_news.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()