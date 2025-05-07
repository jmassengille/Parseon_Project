from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.db.session import Base

if Base is None:
    raise ImportError("Database is not configured. Cannot define ORM models.")

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 