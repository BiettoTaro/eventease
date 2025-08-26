from fastapi import APIRouter, Depends
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import engine
from app.db.database import Base

router = APIRouter()

@router.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/reset-db")
def reset_db(db: Session = Depends(get_db)):
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Database reset"}
    