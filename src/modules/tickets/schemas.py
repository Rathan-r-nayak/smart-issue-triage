from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Any
from src.modules.tickets.constants import TicketStatus, OwnerType

class StatusHistoryResponse(BaseModel):
    status_entry_id: int
    status: TicketStatus
    owner_type: OwnerType  # Matches your new database model attribute!
    assigned_employee_id: Optional[str] = None  # Shows the human ID if assigned
    queue_name: Optional[str] = None            # Shows the queue if escalated
    status_notes: Optional[str] = None
    assigned_at: datetime

    # --- THE FIX: Intercept raw DB strings and fix their casing BEFORE validation ---
    @field_validator("status", mode="before")
    @classmethod
    def clean_status_casing(cls, v: Any) -> Any:
        if isinstance(v, str):
            mapping = {
                "OPEN": "Open",
                "ASSIGNED": "Assigned",
                "RESOLVED": "Resolved",
                "CLOSED": "Closed",
                "RESOLVED_BY_AI": "Resolved_by_AI"
            }
            # Look up the uppercase version, return the Title Case version if found
            return mapping.get(v.upper(), v)
        return v

    @field_validator("owner_type", mode="before")
    @classmethod
    def clean_owner_casing(cls, v: Any) -> Any:
        if isinstance(v, str):
            mapping = {
                "AI": "AI",
                "QUEUE": "Queue",
                "HUMAN": "Human"
            }
            return mapping.get(v.upper(), v)
        return v
    # --------------------------------------------------------------------------------

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    employee_id: str = Field(
        description="The unique identifier of the employee raising the incident or requesting support. E.g., 'EMP12345'."
    )
    
    specific_facility: str = Field(
        description="The physical office location, building, or branch campus where the issue is occurring. E.g., 'Whitefield Campus, Block A'."
    )
    
    catalog_category: str = Field(
        description="The high-level corporate classification domain for the request. Must exactly match a valid catalog category. E.g., 'IT Services', 'Facility Services'."
    )
    
    catalog_item: str = Field(
        description="The specific asset class or technical service group experiencing the fault. Must match a valid system catalog item. E.g., 'Hardware Support', 'Software Licensing', 'HVAC and Temperature Control'."
    )
    
    request_sub_type: Optional[str] = Field(
        default=None,
        description="The granular, specific underlying technical root issue. Use this to pinpoint the exact fault. E.g., 'Laptop Repair', 'Docker Desktop Pro License', 'AC Dripping Water'."
    )
    
    ticket_description: str = Field(
        description="A thorough, detailed explanation of the incident symptoms, errors encountered, business impact, and any troubleshooting actions attempted so far."
    )
    
    callback_consent: Optional[bool] = Field(
        default=True,
        description="Explicit boolean indicator stating whether the reporting employee consents to being contacted directly via phone or internal chat for follow-up verification."
    )

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

class StatusHistoryCreateRequest(BaseModel):
    status: TicketStatus = Field(
        description="The new corporate lifecycle state. Options: 'Open', 'Assigned', 'Resolved', 'Closed'"
    )
    owner_type: OwnerType = Field(
        default=OwnerType.HUMAN,
        description="The actor changing the ticket state. Valid options are: 'AI' (LangGraph), 'Queue' (Unassigned Pool), or 'Human' (IT Support Agent)."
    )
    assigned_employee_id: Optional[str] = Field(
        default=None, 
        description="The ID of the IT Admin claiming or processing the ticket."
    )
    queue_name: Optional[str] = Field(
        default=None, 
        description="The active assignment queue if escalated or transferred. E.g., 'POOL', 'L1_QUEUE'."
    )
    status_notes: Optional[str] = Field(
        default=None, 
        description="Timeline log descriptions explaining why the status changed."
    )
    resolution_summary: Optional[str] = Field(
        default=None, 
        description="Mandatory only when status is 'Resolved'. Explains the exact solution details for AI indexing."
    )