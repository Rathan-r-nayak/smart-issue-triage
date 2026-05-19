from typing import List

from src.modules.tickets.repository import TicketRepository
from src.modules.employees.repository import EmployeeRepository
from src.modules.tickets.schemas import TicketCreate, TicketStatusUpdate
from src.modules.tickets.models import CatalogMasterModel, TicketModel, TicketStatusHistoryModel
from src.modules.tickets.constants import TicketStatus, OwnerType

class TicketService:
    def __init__(self, ticket_repo: TicketRepository, employee_repo: EmployeeRepository):
        self.ticket_repo = ticket_repo
        self.employee_repo = employee_repo

    def create_new_ticket(self, ticket_in: TicketCreate) -> TicketModel:
        # 1. Verify Employee via cross-boundary repository lookup
        employee = self.employee_repo.get_by_id(ticket_in.employee_id)
        if not employee:
            raise ValueError("Invalid employee_id.")

        valid_catalog = self.ticket_repo.db.query(CatalogMasterModel).filter(
            CatalogMasterModel.category == ticket_in.catalog_category,
            CatalogMasterModel.item == ticket_in.catalog_item,
            CatalogMasterModel.sub_type == ticket_in.request_sub_type
        ).first()

        if not valid_catalog:
            raise ValueError(
                f"Invalid catalog combination: "
                f"'{ticket_in.catalog_category}' -> '{ticket_in.catalog_item}' is not a recognized path."
            )

        # 2. Convert incoming Pydantic fields to the core model structure
        new_ticket = TicketModel(**ticket_in.model_dump())
        saved_ticket = self.ticket_repo.save_ticket(new_ticket)

        # 3. Automatically append the initial Draft state history tracking metric
        initial_status = TicketStatusHistoryModel(
            ticket_id=saved_ticket.ticket_id,
            status=TicketStatus.DRAFT,
            owner_type=OwnerType.AI,
            status_notes="Ticket initialized via smart-issue-triage agent."
        )
        self.ticket_repo.save_history(initial_status)
        
        # 4. Finalize transactional state operations atomically
        self.ticket_repo.commit()
        return self.ticket_repo.refresh(saved_ticket)
    

    def update_lifecycle_status(self, ticket_id: int, update_in: TicketStatusUpdate) -> TicketModel:
        """Append a new status tracking row to an existing ticket's history timeline."""
        # 1. Look up target ticket record
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found.")

        # 2. Map input schema to our updated schema variables (owner_type, assigned_employee_id, etc.)
        new_history = TicketStatusHistoryModel(
            ticket_id=ticket_id,
            status=update_in.status,
            owner_type=update_in.owner_type,
            assigned_employee_id=update_in.assigned_employee_id,
            queue_name=update_in.queue_name,
            status_notes=update_in.status_notes
        )
        
        # 3. Save the history record and finalize atomically
        self.ticket_repo.save_history(new_history)
        self.ticket_repo.commit()
        
        return self.ticket_repo.refresh(ticket)

    def list_all_tickets(self) -> List[TicketModel]:
        """Fetch the entire list collection of available tickets."""
        return self.ticket_repo.get_all()
    

    def get_catalog_manifest(self) -> List[CatalogMasterModel]:
        """Retrieve the master classification list for AI agent context routing."""
        return self.ticket_repo.get_all_catalog_items()