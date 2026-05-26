from typing import Optional
import json

from mcp.server.fastmcp import FastMCP

# Ensure these import paths match your actual project structure
# from src.database.session import SessionLocal 
from domains.core.dependencies import SessionLocal
from src.modules.employees.repository import EmployeeRepository
from src.modules.tickets.repository import TicketRepository
from src.modules.tickets.schemas import TicketCreate
from src.modules.tickets.service import TicketService
from src.modules.employees.service import EmployeeService

# 💡 CRITICAL: Import your real, initialized Chroma DB so the agent can search!
from src.modules.config.vector_db import local_vector_store


mcp = FastMCP("Smart Issue Triage Agent")

def get_ticket_service() -> TicketService:
    """Helper to instantiate the Ticket service layer for MCP."""
    db = SessionLocal()
    ticket_repo = TicketRepository(db)
    employee_repo = EmployeeRepository(db)
    return TicketService(ticket_repo, employee_repo, vector_store=local_vector_store)

def get_employee_service() -> EmployeeService:
    """Helper to instantiate the Employee service layer for RAG."""
    return EmployeeService(vector_store=local_vector_store)


@mcp.tool()
def get_ticket_details(ticket_id: int) -> str:
    """Fetch details and current status for a single support ticket. Use this when the user asks for updates."""
    service = get_ticket_service()

    try:
        # Using the repository directly to ensure we get the SQLAlchemy model
        ticket = service.ticket_repo.get_by_id(ticket_id=ticket_id)
        if not ticket:
            return f"Ticket #{ticket_id} not found."
            
        # Manually structuring the string return to prevent Pydantic serialization errors
        return json.dumps({
            "ticket_id": ticket.ticket_id,
            "status": ticket.status,
            "description": ticket.ticket_description,
            "resolution": ticket.resolution_summary
        }, indent=2)
    except Exception as e:
        return f"Error fetching ticket: {e}"
    

@mcp.tool()
def get_employee_tickets(employee_id: str) -> str:
    """Fetch all tickets submitted by a specific employee. Use this to check a user's history."""
    service = get_ticket_service()
    
    try:
        tickets = service.get_employee_ticket_history(employee_id)
        if not tickets:
            return f"No tickets found for employee {employee_id}."
        
        # Format the ticket list into a readable string for the LLM
        result = [
            {"ticket_id": t.ticket_id, "status": t.status, "category": t.catalog_category}
            for t in tickets
        ]
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error fetching employee tickets: {e}"


@mcp.tool()
def create_ticket(
    employee_id: str,
    specific_facility: str,
    catalog_category: str,
    catalog_item: str,
    ticket_description: str,
    request_sub_type: Optional[str] = None,
) -> str:
    """Create a new IT support ticket to escalate an unresolved issue to a human agent."""
    service = get_ticket_service()
    
    try:
        # Safely construct the Pydantic schema internally from the LLM's primitive strings
        ticket_in = TicketCreate(
            employee_id=employee_id,
            specific_facility=specific_facility,
            catalog_category=catalog_category,
            catalog_item=catalog_item,
            ticket_description=ticket_description,
            request_sub_type=request_sub_type,
            callback_consent=True
        )
        
        # Assuming your service layer has this method based on your snippet
        ticket = service.create_new_ticket(ticket_in)
        return f"Success! Escalation Ticket Created. ID: {ticket.ticket_id}"
    except Exception as e:
        return f"Failed to create ticket: {e}"


@mcp.tool()
def search_historical_resolutions(
    query: str, 
    catalog_category: Optional[str] = None, 
    catalog_item: Optional[str] = None
) -> str:
    """
    Search the historical vector database for past resolved tickets. 
    Use this to find how similar issues were fixed in the past.
    """
    service = get_employee_service()

    try:
        # Call the exact method signature we defined in the previous step
        response = service.search_knowledge_base(
            query=query, 
            category=catalog_category, 
            item=catalog_item, 
            limit=3
        )
        
        matches = response.get("matches", [])
        if not matches:
            return "No historical resolutions found for this query."
        
        # Parse the structured dictionary we built in EmployeeService
        formatted_results = []
        for res in matches:
            meta = res["metadata"]
            formatted_results.append(
                f"Past Ticket ID: {meta.get('ticket_id', 'Unknown')}\n"
                f"Category: {meta.get('catalog_category', 'Unknown')} -> {meta.get('catalog_item', 'Unknown')}\n"
                f"Resolution Details: {res['content']}"
            )
            
        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        return f"Vector search failed: {e}"
    


if __name__ == "__main__":
    # Runs via stdio, communicating directly with LangGraph
    mcp.run()