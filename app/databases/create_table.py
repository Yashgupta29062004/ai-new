import sys
from pathlib import Path

# Fix the path to ensure it finds 'app'
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# IMPORTANT: Match your actual folder 'databases' and file 'model'
from app.databases.model import Base 
from app.databases.connection import engine

if __name__ == "__main__":
    print("Connecting to database...")
    # This command actually sends the CREATE TABLE SQL to Postgres
    Base.metadata.create_all(engine)
    print("Tables created successfully!")