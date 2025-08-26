from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os



# Read database url from environment injected by Docker
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/eventease")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastApi routes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
