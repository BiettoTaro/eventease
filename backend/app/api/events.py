from fastapi import APIRouter, HTTPException, Depends
from app.db.database import get_db
from app.schemas.event import EventCreate, EventOut
from app.models.event import Event
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.security import get_current_user
from app.models.user import User
import math


router = APIRouter()

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to create events")
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user),
                radius: Optional[int] = 50,
                ):
    # Fetch first nearby events
    if current_user.latitude and current_user.longitude:
        events = db.query(Event).all()
        nearby = [
            e for e in events if e.latitude and e.longitude and
            haversine(current_user.latitude, current_user.longitude, e.latitude, e.longitude) <= radius_km
        ]
        if nearby:
            return nearby

    # Fallback to same city events
    if current_user.latitude is None and current_user.city:
        city_events = db.query(Event).filter(Event.city == current_user.city).all()
        if city_events:
            return city_events

    # Fallback to same country events
    if current_user.latitude is None and current_user.country:
        country_events = db.query(Event).filter(Event.country == current_user.country).all()
        if country_events:
            return country_events
    
    # Fallback to latest events
    return db.query(Event).order_by(Event.start_time.desc()).all()

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to update events")
    try:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db_event.title = event.title
        db_event.description = event.description
        db_event.start_time = event.start_time
        db_event.end_time = event.end_time
        db_event.latitude = event.latitude
        db_event.longitude = event.longitude
        db_event.city = event.city
        db_event.country = event.country
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update event: { str(e)}")

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to delete events")
    try:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        db.delete(db_event)
        db.commit()
        return {"message": "Event deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: { str(e)}")

# Distance helper function (haversine)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

    
    
 