from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "Open"                       # Ticket registered by user, sitting in POOL
    ASSIGNED = "Assigned"               # Claimed from the pool by an admin/agent
    RESOLVED = "Resolved"               # Fixed by admin (Indexed to historical Vector DB!)
    CLOSED = "Closed"                   # System hard-closed after resolution validation
    
    RESOLVED_BY_AI = "Resolved_by_AI"

class OwnerType(str, Enum):
    AI = "AI"             # Controlled by LangGraph
    QUEUE = "Queue"       # Unassigned in human helpdesk queue
    HUMAN = "Human"       # Assigned to a specific human employee

DEFAULT_QUEUE_NAME = "Tier_1_Support"