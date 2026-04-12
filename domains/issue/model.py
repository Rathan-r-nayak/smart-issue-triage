from domains.core.dependencies import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class IssueDBModel(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    ticket_key = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    issue_type = Column(String, nullable=False) 
    status = Column(String, default="Open")
    custom_metadata = Column(JSONB, default=dict)

    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())