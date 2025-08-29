from fastapi import APIRouter, HTTPException, Depends
from app.db.database import get_db
from app.schemas.registration import RegistrationOut
from app.models.registration import Registration
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.security import get_current_user
from app.models.user import User
from app.models.event import Event
from sqlalchemy.exc import IntegrityError
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/{event_id}", response_model=RegistrationOut)
def register(event_id: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    # Ensure event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already registered
    existing = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered for this event")
                 
    # Check capacity
    if event.capacity:
        count = db.query(Registration).filter(Registration.event_id == event_id).count()
        if count >= event.capacity:
            raise HTTPException(status_code=400, detail="Event is full")
    registration = Registration(user_id=current_user.id, event_id=event_id)
    try:
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Failed to register for event: { str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register for event: { str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register for event: { str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register for event: { str(e)}")
            
@router.get("/event/{event_id}", response_model=list[RegistrationOut])
def get_my_registrations(event_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Registration).filter(Registration.event_id == event_id).all()

@router.delete("/{event_id}")
def unregister(event_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    db.delete(registration)
    db.commit()
    return {"message": "Unregistered from event"}
