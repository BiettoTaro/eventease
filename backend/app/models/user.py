from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    # Geolocation 
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    