import os
from sqlalchemy import create_engine
# FIX: Import from sqlalchemy.orm
from sqlalchemy.orm import sessionmaker 
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_new_aggregator")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# Create the database engine
engine = create_engine(get_database_url(), echo=True)

# FIX: Rename SessionalLocal to SessionLocal to match get_session()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    # This now correctly refers to SessionLocal
    return SessionLocal()