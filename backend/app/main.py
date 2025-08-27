from fastapi import FastAPI
from app.api import auth, users, events, registrations, news, health
from app.services.news_provider import fetch_techcrunch_news
from apscheduler.schedulers.background import BackgroundScheduler
# from app.services.event_provider import fetch_eventbrite_events

app = FastAPI(title="EventEase API", description="API for EventEase", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(registrations.router, prefix="/registrations", tags=["Registrations"])
app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(health.router, prefix="/health", tags=["Health"])


