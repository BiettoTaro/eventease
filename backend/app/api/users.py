from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.models.user import User
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a user
@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    # Create a new user
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        latitude=user.latitude,
        longitude=user.longitude
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# List all users
@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Get a user by id
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.email = user.email
    db_user.name = user.name
    db_user.password_hash = pwd_context.hash(user.password)
    db_user.latitude = user.latitude
    db_user.longitude = user.longitude
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete a user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
