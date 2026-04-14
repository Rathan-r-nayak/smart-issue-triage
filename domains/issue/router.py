from fastapi import APIRouter, HTTPException, status, Depends, Header
from .schema import IssueCreate, IssueResponse
from sqlalchemy.orm import Session
from domains.core.dependencies import get_db
from . import service as svc


router = APIRouter(prefix="/api/v1/ui/tickets", tags=["Issues"])


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(ticket: IssueCreate, x_user_id : str = Header(..., description="Injected by kong API Gateway"), db: Session = Depends(get_db)):
    """
    Creates a new issue (Bug, Story, Task) from the Web UI.
    """
    try:
        new_ticket = svc.create_issue(db, ticket, x_user_id)
        return new_ticket
    except ValueError as ve:
        # Catch our custom Service errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        # Catch unexpected server crashes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while creating the ticket."
        )

