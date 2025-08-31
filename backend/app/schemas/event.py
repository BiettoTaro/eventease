from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import datetime
from typing import List


class EventBase(BaseModel):
    title: str = Field(..., json_schema_extra={'example': "Hackathon 2025"})
    description: str = Field(..., json_schema_extra={'example': "A 48h coding challenge"}) 
    address: Optional[str] = Field(None, json_schema_extra={'example': "Tech Park, Cambridge"})
    city: Optional[str] = Field(None, json_schema_extra={'example': "Cambridge"})
    country: Optional[str] = Field(None, json_schema_extra={'example': "UK"})
    capacity: Optional[int] = Field(None, json_schema_extra={'example': 100})
    latitude: Optional[float] = Field(None, json_schema_extra={'example': 52.2053})
    longitude: Optional[float] = Field(None, json_schema_extra={'example': 0.1218})
    source: Optional[str] = Field(None, json_schema_extra={'example': "Ticketmaster"})
    url: Optional[str] = Field(None, json_schema_extra={'example': "https://ticketmaster.com/event/123"})
    start_time: datetime.datetime = Field(..., json_schema_extra={'example': "2025-09-10T10:00:00Z"})
    end_time: datetime.datetime = Field(..., json_schema_extra={'example': "2025-09-10T18:00:00Z"})

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

