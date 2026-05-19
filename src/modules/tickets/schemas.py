from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from src.modules.tickets.constants import TicketStatus, OwnerType

class StatusHistoryResponse(BaseModel):
    status_entry_id: int
    status: TicketStatus
    owner_type: OwnerType  #  Matches your new database model attribute!
    assigned_employee_id: Optional[str] = None  # Shows the human ID if assigned
    queue_name: Optional[str] = None            # Shows the queue if escalated
    status_notes: Optional[str] = None
    assigned_at: datetime

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
    owner_type: OwnerType  # Updated from assigned_owner to match your database column name
    assigned_employee_id: Optional[str] = None  # Added so you can pass who claimed it
    queue_name: Optional[str] = None            # Added so you can pass which queue it's in
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