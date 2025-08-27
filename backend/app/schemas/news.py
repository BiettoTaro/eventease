from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import datetime


class NewsBase(BaseModel):
    title: str = Field(..., example="News Title")
    summary: Optional[str] = Field(None, example="News Summary")
    url: str = Field(..., example="https://example.com/news")
    image_url: Optional[HttpUrl] = Field(None, example="https://example.com/image.jpg")
    topic: Optional[str] = Field(None, example="News Topic")
    published_at: Optional[datetime.datetime] = Field(None, example="2025-08-27T12:58:51Z")

class NewsCreate(NewsBase):
    pass

class NewsOut(NewsBase):
    id: int
    
    class Config:
        orm_mode = True
        