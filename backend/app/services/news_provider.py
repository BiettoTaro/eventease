import requests
import feedparser
from datetime import datetime
from app.models.news import News
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

TOPIC_KEYWORDS = {
    "AI": ["AI", "artificial intelligence", "machine learning", "neural network"],
    "Cloud": ["cloud", "AWS", "Azure", "GCP"],
    "Security": ["cybersecurity", "hacker", "breach", "malware", "ransomware"],
    "Hardware": ["chip", "processor", "CPU", "GPU", "semiconductor"],
    "Startups": ["startup", "funding", "seed", "venture", "Series A"],
}

def classify_topic(text: str) -> str:
    text_lower = text.lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return topic
    return "General"

def save_news_item(news: News):
    db = SessionLocal()
    existing = db.query(News).filter(News.url == news.url).first()
    if existing:
        db.close()
        return False
    try:
        db.add(news)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save news: {e}")
        return False
    finally:
        db.close()
    return True
    
       

def fetch_techcrunch_news(limit: int = 20):
    url = "https://techcrunch.com/feed/"
    feed = feedparser.parse(url)
    added = 0

    for entry in feed.entries[:limit]:
        # publication date
        published = (
            datetime(*entry.published_parsed[:6])
            if hasattr(entry, "published_parsed")
            else datetime.utcnow()
        )

        # image if available
        image_url = None
        if hasattr(entry, "media_content") and entry.media_content:
            image_url = entry.media_content[0].get("url")

        # log fetched article
        logger.info(f"TC story: {entry.title} ({entry.link})")

        saved = save_news_item(
            News(
            title=entry.title,
            summary=getattr(entry, "summary", None),
            url=entry.link,
            image_url=image_url,
            source="TechCrunch",    
            topic=classify_topic(entry.title),           
            published_at=published
        )
    )

        if saved:
            added += 1
        else:
            logger.info(f"Skipped duplicate: {entry.link}")

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
                News(
                title=story["title"],
                summary=None,
                url=url,
                image_url=None,
                source="HN",        
                topic=classify_topic(story["title"]),        
                published_at=published
            )
        )
            if saved:
                added += 1
            else:
                logger.info(f"Skipped duplicate: {url}")
        else:
            logger.info(f"Skipped invalid story: {story}")
    return added

            
    