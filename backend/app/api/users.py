from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.pagination import PaginatedResponse    
from app.models.user import User
from passlib.context import CryptContext
from app.utils.security import get_current_user

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a user
@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user with email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        # Create a new user
        db_user = User(
            email=user.email,
            name=user.name,
            password_hash=hashed_password,
            latitude=user.latitude,
            longitude=user.longitude,
            city=user.city,
            country=user.country
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# List all users
@router.get("/", response_model=PaginatedResponse[UserOut])
def list_users(db: Session = Depends(get_db),
               limit: int = 10,
               offset: int = 0):
    query = db.query(User)
    return PaginatedResponse(
        total=query.count(),
        limit=limit,
        offset=offset,
        items=query.offset(offset).limit(limit).all()
    )

# Update user location
@router.put("/me/location", response_model=UserOut)
def update_location(
    location: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.latitude = location.get("latitude")
    current_user.longitude = location.get("longitude")
    db.commit()
    db.refresh(current_user)
    return current_user



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
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.email = user.email
        db_user.name = user.name
        db_user.password_hash = pwd_context.hash(user.password)
        db_user.latitude = user.latitude
        db_user.longitude = user.longitude
        db_user.city = user.city
        db_user.country = user.country
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

# Delete a user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
