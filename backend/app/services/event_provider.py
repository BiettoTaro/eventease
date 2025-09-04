import requests, os, feedparser
from app.models.event import Event
from app.db.database import SessionLocal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)    

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_API_BASE_URL = "https://www.searchapi.com/api/v1/search"

def save_event_item(event: Event):
    db = SessionLocal()
    existing = db.query(Event).filter(
        Event.title == event.title,
        Event.url == event.url).first()
    if existing:
        db.close()
        return False
    try:
        db.add(event)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save event: {e}")
        return False
    finally:
        db.close()
    return True


# Fetch events from SearchAPI (google_events)
def fetch_searchapi_events(query="Tech Events", city="London", limit=10, page=1):
    params = {
        "engine": "google_events",
        "q": query,
        "location": city,
        "page": page,
        "api_key": SEARCH_API_KEY
    }
    resp = requests.get(SEARCH_API_BASE_URL, params=params)
    resp.raise_for_status()
    data = resp.json()

    added = 0
    events = data.get("events", [])

    for e in events[:limit]:
        title = e.get("title")
        description = e.get("description", "No description available")
        url = e.get("link")

        # Parse dates
        start = None
        try:
            duration = e.get("duration")
            if e.get("date"):
                day = e["date"].get("day")
                month = e["date"].get("month")
                if day and month:
                    start = datetime.strptime(f"{day} {month} {datetime.now().year}", "%d %b %Y")
        except Exception as err:
            logger.error(f"Failed to parse date for {title}: {err}")
            start = datetime.utcnow()
        
        # Location info
        address = e.get("address")
        location_name = e.get("location")
        venue = e.get("venue", {})
        city = address or location_name
        country = None
        
        # Images
        thumbnail = e.get("thumbnail")
        map_image = e.get("event_location_map", {}).get("image")

        event = Event(
            title=title,
            description=description,
            city=city,
            country=country,
            latitude=None,
            longitude=None,
            source="SearchApi.io",
            url=url,
            start_time=start,
            end_time=None,
            type="Tech Event",
            image=thumbnail,
            map_image=map_image
        )
        logger.info(f"Adding event: {title} ({url}) [{city}, {country}] at {start}")
        if save_event_item(event):
            added += 1
    return added
        
        
        


# Fetch events from Ticketmaster
def fetch_ticketmaster_events(city="London", size=20):
    added = 0

    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "size": size,
    }

    resp = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params)
    resp.raise_for_status()
    data = resp.json()

    if "_embedded" in data and "events" in data["_embedded"]:
        for e in data["_embedded"]["events"]:
            title = e.get("name")
            description = e.get("info", e.get("pleaseNote", "")) or "No description available"
            url = e.get("url")

            # Parse dates
            start = datetime.fromisoformat(
                e["dates"]["start"]["dateTime"].replace("Z", "+00:00")
            )
            end = e["dates"].get("end", {}).get("dateTime")
            if end:
                end = datetime.fromisoformat(end.replace("Z", "+00:00"))
            else:
                end = start + timedelta(hours=2)
            
            # Venue
            venue = e["_embedded"]["venues"][0] if "_embedded" in e and "venues" in e["_embedded"] else {}
            city = venue.get("city", {}).get("name")
            country = venue.get("country", {}).get("name")
            latitude = venue.get("location", {}).get("latitude")
            longitude = venue.get("location", {}).get("longitude")
            
            # Classification
            classification = None
            if "classifications" in e and e["classifications"]:
                class_data = e["classifications"][0]
                # Trying to build type like "music" or "sports"
                segment = class_data.get("segment", {}).get("name")
                genre = class_data.get("genre", {}).get("name")
                classification = " - ".join(filter(None, [segment, genre]))

            # Image
            image = None
            if "images" in e and e["images"]:
                best = [img for img in e["images"] if img.get("ratio") == "16_9" and img.get("width", 0) >= 640]
                image = best[0].get("url") if best else e["images"][0]["url"]
            
            event = Event(
                title=title,
                description=description,
                city=city,
                country=country,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                source="Ticketmaster",
                url=url,
                start_time=start,
                end_time=end,
                type=classification,
                image=image
            )
            logger.info(f"Adding event: {title} ({url}) [{city}, {country}] at {start}")
            if save_event_item(event):
                added += 1
    return added

                
                
            