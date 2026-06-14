import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

db_url = settings.DATABASE_URL

# Robust Fix: If using SQLite, convert any relative path to a deterministic absolute path
if db_url.startswith("sqlite:///"):
    if "./" in db_url:
        # Extract the database filename (e.g., campus_helpdesk.db)
        db_filename = db_url.split("/")[-1]
        
        # Calculate the absolute path to backend/data/ relative to this file's location
        # os.path.dirname(__file__) points to backend/app/, so '..' moves up to backend/
        base_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
        
        # Combine them cleanly and flip Windows backslashes to forward slashes for the URL standard
        full_db_path = os.path.join(base_data_dir, db_filename).replace("\\", "/")
        db_url = f"sqlite:///{full_db_path}"

# For SQLite, 'check_same_thread' must be False to allow async execution
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

# Create the engine with our absolute database URL
engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()