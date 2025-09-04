from fastapi import APIRouter, Depends
from app.db.database import get_db, engine, Base
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    return {"status": "ok"}

@router.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/reset-db")
def reset_db(db: Session = Depends(get_db)):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "ok", "message": "Database reset"}
