from fastapi import APIRouter, HTTPException, status, Depends, Header
from .schema import IssueCreate, IssueResponse
from sqlalchemy.orm import Session
from domains.core.dependencies import get_db
from . import service as svc
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/ui/tickets", tags=["Issues"])


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(ticket: IssueCreate, x_user_id : str = Header(..., description="Injected by kong API Gateway"), db: Session = Depends(get_db)):
    """
    Creates a new issue (Bug, Story, Task) from the Web UI.
    """
    logger.info(f"Received request to create issue from UI for user: {x_user_id}")
    try:
        new_ticket = svc.create_issue(db, ticket, x_user_id)
        logger.info(f"Successfully created issue: {new_ticket.id}")
        return new_ticket
    except ValueError as ve:
        logger.error(f"Validation error creating issue: {str(ve)}")
        # Catch our custom Service errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating issue: {str(e)}")
        # Catch unexpected server crashes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while creating the ticket."
        )

