from fastapi import APIRouter, HTTPException, Depends
from app.db.database import get_db
from app.schemas.event import EventCreate, EventOut
from app.schemas.pagination import PaginatedResponse
from app.models.event import Event
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.utils.security import get_current_user
from app.models.user import User
from datetime import datetime
from app.services.event_provider import fetch_ticketmaster_events, fetch_searchapi_events
from fastapi.encoders import jsonable_encoder
import math


router = APIRouter()

# Helper function to format events response
def format_events(events, limit, offset) -> Dict[str, Any]:
    return {
        "total": len(events),
        "limit": limit,
        "offset": offset,
        "events": [
            {**jsonable_encoder(e), "booking_url": e.url}
            for e in events[offset:offset + limit]
        ]
    }


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
@router.get("/", response_model=PaginatedResponse[EventOut])
def list_events(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
    radius: Optional[int] = 50,
    limit: int = 10, 
    offset: int = 0
):
    query = db.query(Event)
    total = query.count()
    events = query.offset(offset).limit(limit).all()
    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=events
    )

    # # Nearby events first (if user has coordinates)
    # if current_user.latitude and current_user.longitude:
    #     events = query.all()
    #     nearby = [
    #         e for e in events if e.latitude and e.longitude and
    #         haversine(current_user.latitude, current_user.longitude, e.latitude, e.longitude) <= radius
    #     ]
    #     total = len(nearby)
    #     if nearby:
    #         return format_events(nearby, limit, offset)

    # # Fallback to same city
    # if current_user.city:
    #     city_events = query.filter(Event.city == current_user.city).all()
    #     total = len(city_events)
    #     if city_events:
    #         return format_events(city_events, limit, offset)

    # # Fallback to same country
    # if current_user.country:
    #     country_events = query.filter(Event.country == current_user.country).all()
    #     total = len(country_events)
    #     if country_events:
    #         return format_events(country_events, limit, offset)

    # # Final fallback latest events
    # latest = query.order_by(Event.start_time.desc()).all()
    # total = len(latest)
    # return format_events(latest, limit, offset)


# Get event by ID
@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
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
        db_event = db.get(Event, event_id)
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
        db_event = db.get(Event, event_id)
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
        added_searchapi = fetch_searchapi_events()
        added_ticketmaster = fetch_ticketmaster_events()
        return {
            "status": "ok",
            "searchapi": added_searchapi,
            "ticketmaster": added_ticketmaster,

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

    
    
 