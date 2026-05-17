from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.modules.core.database import get_db

# Clean, beautiful Domain-Driven imports
from src.modules.employees.models import EmployeeModel
from src.modules.tickets.models import TicketModel, TicketStatusHistoryModel
from src.modules.tickets.schemas import TicketCreate, TicketResponse, TicketStatusUpdate
from src.modules.tickets.constants import TicketStatus, AssigneeOwner

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    # 1. Verify Employee
    employee = db.query(EmployeeModel).filter(EmployeeModel.employee_id == ticket_in.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Invalid employee_id.")

    # 2. Create Core Ticket
    new_ticket = TicketModel(**ticket_in.model_dump())
    db.add(new_ticket)
    db.flush() # Flushes to get the new ticket_id without committing yet

    # 3. Create the Initial History Status automatically
    initial_status = TicketStatusHistoryModel(
        ticket_id=new_ticket.ticket_id,
        status=TicketStatus.DRAFT,
        assigned_owner=AssigneeOwner.AI_AGENT,
        status_notes="Ticket initialized via smart-issue-triage agent."
    )
    db.add(initial_status)
    
    # 4. Commit transaction atomically
    db.commit()
    db.refresh(new_ticket) 

    return new_ticket

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, update_in: TicketStatusUpdate, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    # Append new status row
    new_history = TicketStatusHistoryModel(
        ticket_id=ticket_id,
        status=update_in.status,
        assigned_owner=update_in.assigned_owner,
        status_notes=update_in.status_notes
    )
    db.add(new_history)
    db.commit()
    db.refresh(ticket)
    
    return ticket

@router.get("/", response_model=List[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    return db.query(TicketModel).order_by(TicketModel.created_at.desc()).all()