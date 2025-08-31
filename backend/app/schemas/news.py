from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional
import datetime


class NewsBase(BaseModel):
    title: str = Field(..., json_schema_extra={'example': "News Title"})
    summary: Optional[str] = Field(None, json_schema_extra={'example': "News Summary"})
    url: str = Field(..., json_schema_extra={'example': "https://example.com/news"})
    image_url: Optional[HttpUrl] = Field(None, json_schema_extra={'example': "https://example.com/image.jpg"})
    source: str = Field(..., json_schema_extra={'example': "News Source"})
    topic: Optional[str] = Field(None, json_schema_extra={'example': "News Topic"})
    published_at: Optional[datetime.datetime] = Field(None, json_schema_extra={'example': "2025-08-27T12:58:51Z"})

class NewsCreate(NewsBase):
    pass

class NewsOut(NewsBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
        