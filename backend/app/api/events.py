from fastapi import APIRouter, HTTPException, Depends
from app.db.database import get_db
from app.schemas.event import EventCreate, EventOut
from app.models.event import Event
from sqlalchemy.orm import Session
from typing import List, Optional
from app.utils.security import get_current_user
from app.models.user import User
from datetime import datetime
from app.services.event_provider import fetch_ticketmaster_events, fetch_university_events
from fastapi.encoders import jsonable_encoder
import math


router = APIRouter()


# Create an event (admin only)
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


# List events (with fallbacks)
@router.get("/", response_model=list[EventOut])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    radius: Optional[int] = 50
):
    events = db.query(Event).all()

    # Nearby events first (if user has coords)
    if current_user.latitude and current_user.longitude:
        nearby = [
            e for e in events if e.latitude and e.longitude and
            haversine(current_user.latitude, current_user.longitude, e.latitude, e.longitude) <= radius
        ]
        if nearby:
            return [
                {**jsonable_encoder(e), "booking_url": e.url}
                for e in nearby
            ]

    # Fallback to same city
    if current_user.city:
        city_events = db.query(Event).filter(Event.location_city == current_user.city).all()
        if city_events:
            return [
                {**jsonable_encoder(e), "booking_url": e.url}
                for e in city_events
            ]

    # Fallback to same country
    if current_user.country:
        country_events = db.query(Event).filter(Event.location_country == current_user.country).all()
        if country_events:
            return [
                {**jsonable_encoder(e), "booking_url": e.url}
                for e in country_events
            ]

    # Final fallback → latest events
    latest = db.query(Event).order_by(Event.start_time.desc()).all()
    return [
        {**jsonable_encoder(e), "booking_url": e.url}
        for e in latest
    ]

# Get event by ID
@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# Update an event (admin only)
@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, event: EventCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to update events")
    try:
        db_event = db.query(Event).filter(Event.id == event_id).first()
        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")
        for field, value in event.dict().items():
            setattr(db_event, field, value)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update event: { str(e)}")

# Delete an event (admin only)
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

# Refresh from third party providers
@router.post("/refresh")
def refresh_events(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to refresh events")

    try:
        added_ticketmaster = fetch_ticketmaster_events()
        added_university = fetch_university_events(
            "https://www.cl.cam.ac.uk/seminars/rss.xml", source="Cambridge CS"
            )
        return {
            "status": "ok",
            "ticketmaster": added_ticketmaster,
            "university": added_university
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh events: { str(e)}")

# Distance helper function (haversine)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

    
    
 