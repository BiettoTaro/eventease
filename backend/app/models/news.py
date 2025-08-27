from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.database import Base
import datetime

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    url = Column(String, nullable=False) # Original source
    image_url = Column(String, nullable=True) # Image URL
    topic = Column(String, nullable=True) # e.g AI, Cloud, Security    
    published_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc)) # Published date