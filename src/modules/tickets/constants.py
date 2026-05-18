from enum import Enum

class TicketStatus(str, Enum):
    DRAFT = "Draft"
    OPEN = "Open"
    IN_PROGRESS = "In_Progress"
    RESOLVED_BY_AI = "Resolved_by_AI"
    ESCALATED = "Escalated"

class OwnerType(str, Enum):
    AI = "AI"             # Controlled by LangGraph
    QUEUE = "Queue"       # Unassigned in human helpdesk queue
    HUMAN = "Human"       # Assigned to a specific human employee

DEFAULT_QUEUE_NAME = "Tier_1_Support"