from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.modules.core.database import get_db

# Clean, beautiful Domain-Driven imports
from src.modules.employees.models import EmployeeModel
from src.modules.tickets.models import TicketModel, TicketStatusHistoryModel
from src.modules.tickets.schemas import TicketCreate, TicketResponse, TicketStatusUpdate
from src.modules.tickets.constants import TicketStatus, OwnerType


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.core.database import get_db
from src.modules.tickets.schemas import TicketCreate, TicketResponse
from src.modules.tickets.repository import TicketRepository
from src.modules.employees.repository import EmployeeRepository
from src.modules.tickets.service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# Dependency Injection Factory Framework
def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    ticket_repo = TicketRepository(db)
    employee_repo = EmployeeRepository(db)
    return TicketService(ticket_repo, employee_repo)

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: TicketCreate, service: TicketService = Depends(get_ticket_service)):
    try:
        return service.create_new_ticket(ticket_in)
    except ValueError as e:
        # Gracefully handle missing/invalid data references with a clean 404
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Fallback mechanism for unexpected parsing failures
        raise HTTPException(status_code=400, detail=str(e))
    


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def transit_ticket_status(ticket_id: int, update_in: TicketStatusUpdate, service: TicketService = Depends(get_ticket_service)):
    try:
        return service.update_lifecycle_status(ticket_id, update_in)
    except ValueError as e:
        # Map missing record exception cleanly to a 404
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TicketResponse])
def get_all_tickets(service: TicketService = Depends(get_ticket_service)):
    # Automatically returns an empty list [] with HTTP 200 if no rows exist
    return service.list_all_tickets()


@router.get("/catalog-options", response_model=List[dict])
def get_available_catalog(service: TicketService = Depends(get_ticket_service)):
    """
    Exposes all valid database catalog paths.
    Your LangGraph AI agent calls this endpoint to update its memory 
    with consistent classification options before executing a ticket creation.
    """
    catalog_items = service.get_catalog_manifest()
    
    # Format the response cleanly so it's easy for an LLM to parse out
    return [
        {
            "id": item.id,
            "catalog_category": item.category,
            "catalog_item": item.item,
            "request_sub_type": item.sub_type
        }
        for item in catalog_items
    ]