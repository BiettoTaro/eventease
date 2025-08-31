from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from typing import Optional
import string

class UserBase(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={'example': "test@example.com"})
    name: str = Field(..., json_schema_extra={'example': "Test Icolo"})
    latitude: Optional[float] = Field(None, json_schema_extra={'example': 51.5074})
    longitude: Optional[float] = Field(None, json_schema_extra={'example': -0.1278})
    city: Optional[str] = Field(None, json_schema_extra={'example': "London"})
    country: Optional[str] = Field(None, json_schema_extra={'example': "UK"})

class UserCreate(UserBase):
    password: str = Field(..., json_schema_extra={'example': "Test123!"})

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in string.punctuation for c in v):
            raise ValueError("Password must contain at least one special character")
        return v
    

class UserOut(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)
        