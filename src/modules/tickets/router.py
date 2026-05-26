from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.modules.employees.router import get_employee_service
from src.modules.employees.service import EmployeeService
from src.modules.core.database import get_db
from src.modules.core.logger import get_logger

# Clean, beautiful Domain-Driven imports
from src.modules.tickets.schemas import KnowledgeBaseResponse, TicketCreate, TicketResponse, TicketStatusUpdate
from src.modules.tickets.repository import TicketRepository
from src.modules.employees.repository import EmployeeRepository
from src.modules.tickets.service import TicketService
from src.modules.config.vector_db import local_vector_store


logger = get_logger(__name__)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# Dependency Injection Factory Framework
def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    ticket_repo = TicketRepository(db)
    employee_repo = EmployeeRepository(db)
    return TicketService(ticket_repo, employee_repo, vector_store=local_vector_store)


# 1. Create Ticket
@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: TicketCreate, service: TicketService = Depends(get_ticket_service)):
    logger.info(f"Received request to create ticket for user: {ticket_in.employee_id}")
    try:
        ticket = service.create_new_ticket(ticket_in)
        logger.info(f"Successfully created ticket: {ticket.ticket_id}")
        return ticket
    except ValueError as e:
        logger.error(f"Validation error creating ticket: {str(e)}")
        # Gracefully handle missing/invalid data references with a clean 404
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error creating ticket: {str(e)}")
        # Fallback mechanism for unexpected parsing failures
        raise HTTPException(status_code=400, detail=str(e))


# 2. Update Status
# @router.patch("/{ticket_id}/status", response_model=TicketResponse)
# def transit_ticket_status(ticket_id: int, update_in: TicketStatusUpdate, service: TicketService = Depends(get_ticket_service)):
#     logger.info(f"Received request to update status for ticket: {ticket_id}")
#     try:
#         ticket = service.update_lifecycle_status(ticket_id, update_in)
#         logger.info(f"Successfully updated status for ticket: {ticket_id}")
#         return ticket
#     except ValueError as e:
#         logger.error(f"Validation error updating ticket {ticket_id}: {str(e)}")
#         # Map missing record exception cleanly to a 404
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         logger.exception(f"Unexpected error updating ticket {ticket_id}: {str(e)}")
#         raise HTTPException(status_code=400, detail=str(e))


# 3. Get ALL Tickets (Human UI only, NOT for AI)
@router.get("/", response_model=List[TicketResponse])
def get_all_tickets(service: TicketService = Depends(get_ticket_service)):
    logger.info("Fetching all tickets")
    # Automatically returns an empty list [] with HTTP 200 if no rows exist
    return service.list_all_tickets()


# 4. Catalog Options
@router.get("/catalog-options", response_model=List[dict])
def get_available_catalog(service: TicketService = Depends(get_ticket_service)):
    """
    Exposes all valid database catalog paths.
    Your LangGraph AI agent calls this endpoint to update its memory 
    with consistent classification options before executing a ticket creation.
    """
    logger.info("Fetching available catalog options")
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



@router.get("/search-solutions", response_model=KnowledgeBaseResponse, status_code=status.HTTP_200_OK)
def search_historical_solutions(
    query: str = Query(..., description="The user's problem statement (e.g., 'My laptop screen is flickering')"),
    catalog_category: Optional[str] = Query(None, description="Filter by main category (e.g., 'IT Services')"),
    catalog_item: Optional[str] = Query(None, description="Filter by item (e.g., 'Hardware Support')"),
    request_sub_type: Optional[str] = Query(None, description="Filter by specific sub-type"),
    limit: int = Query(3, ge=1, le=10, description="Number of historical solutions to return"),
    service: TicketService = Depends(get_ticket_service)
):
    """
    **Semantic Knowledge Base Search**
    
    Searches past resolved tickets to provide immediate self-service solutions to employees.
    Uses Hugging Face embeddings and strict metadata filtering for high precision.
    """
    return service.search_knowledge_base(
        query=query,
        category=catalog_category,
        item=catalog_item,
        sub_type=request_sub_type,
        limit=limit
    )


# search filters
@router.get("/search/query", response_model=List[TicketResponse])
def search_tickets_registry(
    employee_id: Optional[str] = Query(None, description="Filter by the raising employee's ID"),
    description: Optional[str] = Query(None, description="Fuzzy text search string inside ticket summaries"),
    service: TicketService = Depends(get_ticket_service)
):
    """
    Dynamic endpoint allowing semantic or exact filtering.
    Enables calls like: /api/tickets/search/query?description=db
    or /api/tickets/search/query?employee_id=123456
    """
    try:
        return service.find_tickets(employee_id=employee_id, description_query=description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))# 5. Get by ID
    



# 5. Get by ID
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_by_id(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    """Fetch details for a single target ticket."""
    try:
        return service.get_ticket_by_id(ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/employee/{employee_id}", response_model=List[TicketResponse], status_code=status.HTTP_200_OK)
def get_tickets_by_employee_id(
    employee_id: str,
    service: TicketService = Depends(get_ticket_service)
):
    """
    **Fetch Employee Tickets**
    
    Returns a list of all tickets (including their status history) 
    created by a specific employee ID. 
    """
    return service.get_employee_ticket_history(employee_id)