from pydantic import BaseModel, ConfigDict
import datetime

class RegistrationOut(BaseModel):
    id: int
    user_id: int
    event_id: int
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)