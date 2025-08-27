from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from app.db.database import Base
from sqlalchemy.orm import relationship
import datetime

class Registration(Base):
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    # Prevent duplicate registrations
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="unique_registration"),)
    