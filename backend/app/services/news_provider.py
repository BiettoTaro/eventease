import requests
import feedparser
from datetime import datetime
from app.models.news import News
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


def save_news_item(title, summary, url, image_url, topic, published_at):
    db = SessionLocal()
    existing = db.query(News).filter(News.url == url).first()
    if existing:
        db.close()
        return False
    news_item = News(
        title=title,
        summary=summary,
        url=url,
        image_url=image_url,
        topic=topic,
        published_at=published_at
    )
    db.add(news_item)
    db.commit()
    db.close()
    return True

def fetch_techcrunch_news():
    url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(url)
    added = 0

    for entry in feed.entries:
        # Skip if already in db
        published = datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") else datetime.utcnow()
        if save_news_item(entry.title, entry.summary, entry.link, entry.get("media_content", [{}])[0].get("url")
             if hasattr(entry, "media_content") else None, "Tech", published):
            added += 1
    return added

def fetch_hackernews_news(limit: int = 10):
    base = "https://hacker-news.firebaseio.com/v0"
    fallback_url = "https://news.ycombinator.com/item?id="
    ids = requests.get(f"{base}/topstories.json").json()[:limit]
    added = 0

    for story_id in ids:
        story = requests.get(f"{base}/item/{story_id}.json").json()
        if story and "title" in story:
            # Use provided URL or fallback to HN discussion link
            url = story.get("url") or f"{fallback_url}{story_id}"
            published = datetime.utcfromtimestamp(story["time"])
            logger.info(f"HN story: {story['title']} ({url})")   
            saved = save_news_item(
                title=story["title"],
                summary=None,
                url=url,
                image_url=None,
                topic="HN",        
                published_at=published
            )
            if saved:
                added += 1
            else:
                logger.info(f"Skipped duplicate: {url}")
        else:
            logger.info(f"Skipped invalid story: {story}")
    return added

            
    