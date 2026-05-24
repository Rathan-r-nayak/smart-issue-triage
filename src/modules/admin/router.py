# src/modules/admin/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import your database session dependency, service layers, and request schemas
from src.modules.tickets.service import TicketService
from src.modules.tickets.schemas import StatusHistoryCreateRequest
from src.modules.tickets.repository import TicketRepository  # Adjust based on your setup
from src.modules.employees.repository import EmployeeRepository  # Adjust based on your setup
from src.modules.core.database import get_db


router = APIRouter(
    prefix="/api/admin/tickets",
    tags=["🛡️ Admin Ticket Management"]
)

# Dependency Factory to instantiate your TicketService with its repositories
def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    ticket_repo = TicketRepository(db)
    employee_repo = EmployeeRepository(db)
    
    # Inject your Vector Store client instance here if initialized globally
    # e.g., from src.config.vector_db import azure_vector_store
    vector_store = getattr(db, "vector_store", None) 
    
    return TicketService(ticket_repo=ticket_repo, employee_repo=employee_repo, vector_store=vector_store)


@router.post("/{ticket_id}/status", status_code=status.HTTP_200_OK)
def update_ticket_status_by_admin(
    ticket_id: int,
    payload: StatusHistoryCreateRequest,
    service: TicketService = Depends(get_ticket_service)
):
    """
    **Transition a ticket state as an Administrator.**
    
    This endpoint appends a new state tracking log to the status history timeline. 
    If the status is shifted to **'Resolved'**, it captures the resolution details and 
    automatically schedules background vectorization for the LangGraph agent knowledge base.
    """
    try:
        updated_ticket = service.admin_transit_ticket_status(
            ticket_id=ticket_id, 
            update_data=payload
        )
        
        return {
            "success": True,
            "message": f"Ticket #{ticket_id} successfully transitioned to '{payload.status}'.",
            "ticket_id": updated_ticket.ticket_id,
            "current_resolution_summary": updated_ticket.resolution_summary
        }
        
    except ValueError as val_err:
        # Handles missing ticket IDs (404) or missing resolution summaries (400) cleanly
        error_msg = str(val_err)
        if "not found" in error_msg or "does not exist" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
        
    except Exception as e:
        # Failsafe catch-all boundary for unhandled server issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during state transition processing: {str(e)}"
        )