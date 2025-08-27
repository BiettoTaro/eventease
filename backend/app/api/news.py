from fastapi import APIRouter, HTTPException, Depends
from app.db.database import get_db
from app.schemas.news import NewsCreate, NewsOut
from app.models.news import News
from sqlalchemy.orm import Session
from typing import List
from app.utils.security import get_current_user
from app.models.user import User
from app.services.news_provider import fetch_techcrunch_news

router = APIRouter()

@router.post("/", response_model=NewsOut)
def create_news(news: NewsCreate, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to create news")
    try:
        db_news = News(
        title=news.title,
        summary=news.summary,
        url=str(news.url),
        image_url=str(news.image_url) if news.image_url else None,
        topic=news.topic,
        published_at=news.published_at
    )
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create news: { str(e)}")

@router.get("/", response_model=list[NewsOut])
def list_news(topic: str = None, db: Session = Depends(get_db)):
    query = db.query(News)
    if topic:
        query = query.filter(News.topic == topic)
    return query.all()

@router.put("/{news_id}", response_model=NewsOut)
def update_news(news_id: int, news: NewsCreate, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update news")
    try:
        db_news = db.query(News).filter(News.id == news_id).first()
        if not db_news:
            raise HTTPException(status_code=404, detail="News not found")
        db_news.title = news.title
        db_news.summary = news.summary
        db_news.url = str(news.url)
        db_news.image_url = str(news.image_url) if news.image_url else None
        db_news.topic = news.topic
        db_news.published_at = news.published_at
        db.commit()
        db.refresh(db_news)
        return db_news
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update news: { str(e)}")

@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete news")
    try:
        db_news = db.query(News).filter(News.id == news_id).first()
        if not db_news:
            raise HTTPException(status_code=404, detail="News not found")
        db.delete(db_news)
        db.commit()
        return {"message": "News deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete news: { str(e)}")


@router.post("/refresh")
def refresh_news(db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to refresh news")
    try:
        added = fetch_techcrunch_news()
        return {"message": f"Refreshed news, added {added} new items"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh news: { str(e)}")