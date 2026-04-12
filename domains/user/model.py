from sqlalchemy import Column, String, DateTime
from domains.core.dependencies import Base
from sqlalchemy.sql import func


class UserDBModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index= True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="developer")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())