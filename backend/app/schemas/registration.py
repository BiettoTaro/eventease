from pydantic import BaseModel
import datetime

class RegistrationOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True