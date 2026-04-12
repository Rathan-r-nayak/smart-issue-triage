from fastapi import APIRouter, status, Depends
from .schema import IssueCreate, IssueResponse
from sqlalchemy.orm import Session
from core.dependencies import get_db
# from core.dep


router = APIRouter(prefix="/api/v1/ui/tickets", tags=["Issues"])


@router.post("/" response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(ticket: IssueCreate, db: Session = Depends(get_db)):
    """
    Creates a new issue (Bug, Story, Task) from the Web UI.
    """
    try:
        # new_ticket = create_issue