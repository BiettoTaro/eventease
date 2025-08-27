import requests
import feedparser
from datetime import datetime
from app.models.news import News
from app.db.database import SessionLocal

def fetch_techcrunch_news():
    url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(url)

    db = SessionLocal()
    added = 0
    for entry in feed.entries:
        # Skip if already in db
        existing = db.query(News).filter(News.url == entry.link).first()
        if existing:
            continue
        
        # Create new news item
        news_item = News(
            title=entry.title,
            summary=entry.summary if hasattr(entry, "summary") else None,
            url=entry.link,
            image_url=entry.get("media_content", [{}])[0].get("url")
             if hasattr(entry, "media_content") else None,
            topic="Tech",
            published_at=datetime(*entry.published_parsed[:6]) 
             if hasattr(entry, "published_parsed") else datetime.utcnow() 
        )
        db.add(news_item)
        added += 1
    db.commit()
    db.close()
    return added
    