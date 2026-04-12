from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
import datetime

class IssuetypeEnum(str, Enum):
    bug = "Bug"
    story = "Story"
    task = "Task"


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(...)
    issue_type: IssuetypeEnum = Field(...)
    assignee_id = Optional[str] = Field(None, description="The user ID of the person working on this")
    custom_metadata: Optional[dict] = Field(default_factory=dict)

class IssueResponse(IssueCreate):
    id: int
    ticket_key: str
    status: str
    reporter_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)