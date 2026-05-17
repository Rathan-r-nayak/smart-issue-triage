from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from src.modules.tickets.constants import TicketStatus, AssigneeOwner

class StatusHistoryResponse(BaseModel):
    status_entry_id: int
    status: TicketStatus
    assigned_owner: AssigneeOwner
    assigned_at: datetime
    status_notes: Optional[str]

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    employee_id: str
    specific_facility: str
    catalog_category: str
    catalog_item: str
    request_sub_type: Optional[str] = None
    ticket_description: str
    callback_consent: Optional[bool] = True

class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    assigned_owner: AssigneeOwner
    status_notes: Optional[str] = None

class TicketResponse(BaseModel):
    ticket_id: int
    employee_id: str
    specific_facility: str
    catalog_category: str
    catalog_item: str
    ticket_description: str
    callback_consent: bool
    resolution_summary: Optional[str]
    created_at: datetime
    
    # Automatically nests the history timeline when returning the JSON!
    status_history: List[StatusHistoryResponse] = []

    class Config:
        from_attributes = True