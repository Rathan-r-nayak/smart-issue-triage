from typing import Optional

from mcp.server.fastmcp import FastMCP
from modules.employees.repository import EmployeeRepository
from modules.tickets.repository import TicketRepository
from modules.tickets.schemas import TicketCreate
from src.modules.core.database import SessionLocal 
from modules.tickets.service import TicketService



mcp = FastMCP("Smart Issue Triage Agent")


def get_ai_service() -> TicketService:
    """Helper to instantiate the service layer for MCP without HTTP Depends."""
    db = SessionLocal()
    ticket_repo = TicketRepository(db)
    employee_repo = EmployeeRepository(db)

    return TicketService(ticket_repo, employee_repo, vector_store=None)


@mcp.tool()
def get_ticket_details(ticket_id: int) -> str:
    """Fetch details and current status for a single support ticket. Use this when the user asks for updates."""
    service = get_ai_service()

    try:
        ticket = service.get_ticket_by_id(ticket_id= ticket_id)
        return str(ticket.model_dump())
    except Exception as e:
        return f"Error fetching ticket: {e}"
    

@mcp.tool()
def create_ticket(ticket_in: TicketCreate) -> str:
    """Create a new IT support ticket to escalate an unresolved issue to a human agent."""
    service = get_ai_service()
    
    try:
        ticket = service.create_new_ticket(ticket_in)
        return f"Success! Escalation Ticket Created. ID: {ticket.ticket_id}"
    except Exception as e:
        return f"Failed to create ticket: {e}"


@mcp.tool()
def search_historical_resolutions(query: str, category: Optional[str] = None, ticket_id: Optional[str] = None) -> str:
    """
    Search the historical vector database for past resolved tickets. 
    Use this to find how similar issues were fixed in the past.
    """
    service = get_ai_service()

    try:
        results = service.search_knowledge_base(query, ticket_id, category)

        if not results:
            return "No historical resolutions found for this query."
        
        formatted_results = "\n\n".join([
            f"Past Ticket ID: {res.metadata.get('ticket_id', 'Unknown')}\n"
            f"Category: {res.metadata.get('category', 'Unknown')}\n"
            f"Resolution: {res.page_content}"
            for res in results
        ])
        return formatted_results
    except Exception as e:
        return f"Vector search failed: {e}"
    
if __name__ == "__main__":
    # Runs via stdio, communicating directly with LangGraph
    mcp.run()