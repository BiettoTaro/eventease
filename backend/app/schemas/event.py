from pydantic import BaseModel, Field
from typing import Optional
import datetime


class EventBase(BaseModel):
    title: str = Field(..., example="Hackathon 2025")
    description: str = Field(..., example="A 48h coding challenge") 
    address: Optional[str] = Field(None, example="Tech Park, Cambridge")
    city: Optional[str] = Field(None, example="Cambridge")
    country: Optional[str] = Field(None, example="UK")
    latitude: Optional[float] = Field(None, example=52.2053)
    longitude: Optional[float] = Field(None, example=0.1218)
    start_time: datetime.datetime = Field(..., example="2025-09-10T10:00:00Z")
    end_time: datetime.datetime = Field(..., example="2025-09-10T18:00:00Z")

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    
    class Config:
        orm_mode = True