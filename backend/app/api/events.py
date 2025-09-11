from fastapi import APIRouter, HTTPException, Depends, Query
from app.db.database import get_db
from app.schemas.event import EventCreate, EventOut
from app.schemas.pagination import PaginatedResponse
from app.models.event import Event
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.utils.security import get_current_user
from app.models.user import User
from app.services.event_provider import fetch_ticketmaster_events, fetch_searchapi_events
from fastapi.encoders import jsonable_encoder
import math
from sqlalchemy import or_ , case, func



router = APIRouter()

# Helper function to format events response
def format_events(events, limit, offset) -> Dict[str, Any]:
    return {
        "total": len(events),
        "limit": limit,
        "offset": offset,
        "items": [
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
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# List events (with fallbacks)
@router.get("/", response_model=PaginatedResponse[EventOut])
def list_events(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    radius: Optional[int] = 50,
    limit: int = 10,
    offset: int = 0
):
    query = db.query(Event)

    # Apply search filters
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Event.title.ilike(like),
                Event.description.ilike(like),
                Event.city.ilike(like),
                Event.type.ilike(like)
            )
        )

    all_events = query.all()

    # Split sources
    searchapi_events = [e for e in all_events if e.source and e.source.lower() == "searchapi.io"]
    other_events = [e for e in all_events if not e.source or e.source.lower() != "searchapi.io"]

    # Sort each group by start_time descending
    searchapi_events.sort(key=lambda e: e.start_time or datetime.min, reverse=True)
    other_events.sort(key=lambda e: e.start_time or datetime.min, reverse=True)

    # Combine with SearchApi.io always first
    combined = searchapi_events + other_events

    total = len(combined)

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=combined[offset:offset+limit]
    )




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
    
    db_event = db.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    try:
        for field, value in event.model_dump().items():
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
    
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted"}


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