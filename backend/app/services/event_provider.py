import requests, os, feedparser
from app.models.event import Event
from app.db.database import SessionLocal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)    

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

def save_event_item(event: Event):
    db = SessionLocal()
    existing = db.query(Event).filter(Event.url == event.url).first()
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


# Fetch events from Ticketmaster
def fetch_ticketmaster_events(city="London", size=10):
    added = 0
    db = SessionLocal()

    # Prioritized queries
    queries = [
        {"classificationName": "Science & Tech"},
        {"keyword": "technology"},
        {"keyword": "conference"},
        {},  # fallback: all events in London
    ]

    for query in queries:
        params = {"apikey": TICKETMASTER_API_KEY, "city": city, "size": size, **query}
        resp = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params)
        data = resp.json()

        if "_embedded" in data and "events" in data["_embedded"]:
            for e in data["_embedded"]["events"]:
                title = e["name"]
                description = e.get("info", e.get("pleaseNote", "")) or "No description"
                url = e.get("url")
                start_time = datetime.fromisoformat(e["dates"]["start"]["dateTime"].replace("Z", "+00:00"))
                end_time_str = e["dates"].get("end", {}).get("dateTime")
                if end_time_str:
                    end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                else:
                    end_time = start_time + timedelta(hours=2)

                venue = e["_embedded"]["venues"][0] if "_embedded" in e and "venues" in e["_embedded"] else {}
                city = venue.get("city", {}).get("name")
                country = venue.get("country", {}).get("name")
                latitude = venue.get("location", {}).get("latitude")
                longitude = venue.get("location", {}).get("longitude")

                event = Event(
                    title=title,
                    description=description,
                    city=city,
                    country=country,
                    latitude=float(latitude) if latitude else None,
                    longitude=float(longitude) if longitude else None,
                    source="Ticketmaster",
                    url=url,
                    start_time=start_time,
                    end_time=end_time,
                )
                logger.info(f"Adding event: {title} ({url}) [{city}, {country}] at {start_time}")
                if save_event_item(event):
                    added += 1
            break  #  Stop after first successful non-empty fetch

    db.close()
    return added
            
# University/conventions events
def fetch_university_events(feed_url, source="University", limit=10):
    feed = feedparser.parse(feed_url)
    added = 0
    for entry in feed.entries[:limit]:  
        start = datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.utcnow()
        logger.info(f"Adding event: {entry.title} ({entry.link}) [{entry.city}, {entry.country}] at {start}")

        if save_event_item(Event(
            title=entry.title,
            description=entry.get("summary", ""),
            start_time=start,
            end_time=None,
            city=entry.city,
            country=entry.country,
            latitude=entry.latitude,
            longitude=entry.longitude,
            source=source,
            url=entry.link,
        )):
            added += 1
    return added