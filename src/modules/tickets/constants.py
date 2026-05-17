from enum import Enum

class TicketStatus(str, Enum):
    DRAFT = "Draft"
    OPEN = "Open"
    IN_PROGRESS = "In_Progress"
    RESOLVED_BY_AI = "Resolved_by_AI"
    ESCALATED = "Escalated"

class AssigneeOwner(str, Enum):
    AI = "AI"             # Owned by the LangGraph Agent
    QUEUE = "Queue"       # Sitting unassigned in a human queue
    HUMAN = "Human"

# Local defaults for the ticket domain
DEFAULT_CALLBACK_CONSENT = True