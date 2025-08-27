from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.utils.security import verify_password, create_access_token
from app.models.user import User
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, Field

router = APIRouter()

class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@eventease.com")
    password: str = Field(..., example="Admin@123")

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Step 1: Look up user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Step 2: Verify password
    try:
        valid = verify_password(payload.password, user.password_hash)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password verification failed",
        )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Step 3: Issue JWT
    try:
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token generation failed: {str(e)}",
        )

    return {"access_token": access_token, "token_type": "bearer"}