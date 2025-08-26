from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.utils.security import verify_password, create_access_token
from app.models.user import User
from sqlalchemy.orm import Session
from datetime import timedelta

router = APIRouter()

@router.post("/login")
def login(username:str, password:str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}