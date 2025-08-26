from fastapi import APIRouter, Depends
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()

@router.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
