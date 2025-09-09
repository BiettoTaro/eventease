from fastapi import FastAPI
from app.api import auth, users, events, registrations, news, health
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI(title="EventEase API", description="API for EventEase", version="1.0.0")

# CORS setup
origins = [
    "http://localhost:3000",  # Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(registrations.router, prefix="/registrations", tags=["Registrations"])
app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(health.router, prefix="/health", tags=["Health"])
