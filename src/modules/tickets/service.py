from datetime import datetime
from typing import List, Optional
from src.modules.core.logger import get_logger

from src.modules.tickets.repository import TicketRepository
from src.modules.employees.repository import EmployeeRepository
from src.modules.tickets.schemas import StatusHistoryCreateRequest, TicketCreate, TicketStatusUpdate
from src.modules.tickets.models import CatalogMasterModel, TicketModel, TicketStatusHistoryModel
from src.modules.tickets.constants import TicketStatus, OwnerType

logger = get_logger(__name__)

class TicketService:
    def __init__(self, ticket_repo: TicketRepository, employee_repo: EmployeeRepository, vector_store=None):
        self.ticket_repo = ticket_repo
        self.employee_repo = employee_repo
        self.vector_store = vector_store



    def create_new_ticket(self, ticket_in: TicketCreate) -> TicketModel:
        logger.info(f"Creating new ticket for employee {ticket_in.employee_id}")
        # 1. Verify Employee via cross-boundary repository lookup
        employee = self.employee_repo.get_by_id(ticket_in.employee_id)
        if not employee:
            logger.error(f"Failed to create ticket: Invalid employee_id {ticket_in.employee_id}")
            raise ValueError("Invalid employee_id.")

        valid_catalog = self.ticket_repo.db.query(CatalogMasterModel).filter(
            CatalogMasterModel.category == ticket_in.catalog_category,
            CatalogMasterModel.item == ticket_in.catalog_item,
            CatalogMasterModel.sub_type == ticket_in.request_sub_type
        ).first()

        if not valid_catalog:
            logger.error(f"Invalid catalog combination: {ticket_in.catalog_category} -> {ticket_in.catalog_item}")
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
            status=TicketStatus.OPEN,
            owner_type=OwnerType.AI,
            status_notes="Ticket initialized via smart-issue-triage agent."
        )
        self.ticket_repo.save_history(initial_status)
        
        # 4. Finalize transactional state operations atomically
        self.ticket_repo.commit()
        logger.info(f"Ticket {saved_ticket.ticket_id} created successfully")
        return self.ticket_repo.refresh(saved_ticket)
    

    def update_lifecycle_status(self, ticket_id: int, update_in: TicketStatusUpdate) -> TicketModel:
        """Append a new status tracking row to an existing ticket's history timeline."""
        logger.info(f"Updating status for ticket {ticket_id} to {update_in.status}")
        # 1. Look up target ticket record
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found for status update")
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
        
        logger.info(f"Ticket {ticket_id} status updated to {update_in.status}")
        return self.ticket_repo.refresh(ticket)

    def list_all_tickets(self) -> List[TicketModel]:
        """Fetch the entire list collection of available tickets."""
        return self.ticket_repo.get_all()
    

    def get_catalog_manifest(self) -> List[CatalogMasterModel]:
        """Retrieve the master classification list for AI agent context routing."""
        return self.ticket_repo.get_all_catalog_items()
    


    def get_ticket_by_id(self, ticket_id: int) -> Optional[TicketModel]:
        """Retrieve a specific ticket."""
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket with ID {ticket_id} does not exist.")
        return ticket

    def find_tickets(self, employee_id: Optional[str] = None, description_query: Optional[str] = None) -> List[TicketModel]:
        """Orchestrate the search parameters for the repository lookup layer."""
        return self.ticket_repo.search_tickets(employee_id=employee_id, description_query=description_query)
        

    def search_knowledge_base(self, query: str, ticket_id: Optional[str] = None, category: Optional[str] = None) -> list:
        """Queries the Vector DB for past resolved tickets."""
        if not self.vector_store:
            raise ValueError("Vector store is not initialized.")
        
        filters = {}
        if ticket_id: 
            filters["ticket_id"] = ticket_id
        if category: 
            filters["category"] = category


        results = self.vector_store.similarity_search(
            query = query,
            k = 3,
            filter = filters if filters else None
        )

        return results
    

    # update the ticket status
    def admin_transit_ticket_status(self, ticket_id: int, update_data: StatusHistoryCreateRequest) -> TicketModel:
        """
        Transition a ticket to a new state by an Administrator.
        Validation is handled by Pydantic; PostgreSQL stores standard strings.
        """
        ticket = self.ticket_repo.get_by_id(ticket_id)

        if not ticket:
            raise ValueError(f"Ticket #{ticket_id} not found.")

        # update_data.status is validated by Pydantic against your Python Enum.
        # We just safely extract the underlying string value (e.g., "Resolved").
        target_status_str = update_data.status.value if hasattr(update_data.status, 'value') else str(update_data.status)
        target_owner_str = update_data.owner_type.value if hasattr(update_data.owner_type, 'value') else str(update_data.owner_type)

        if target_status_str == "Resolved":
            if not update_data.resolution_summary or not update_data.resolution_summary.strip():
                raise ValueError("A detailed resolution_summary is required to resolve a ticket.")
            ticket.resolution_summary = update_data.resolution_summary

        # Save directly to the database without fighting constraints
        new_history_entry = TicketStatusHistoryModel(
            ticket_id=ticket.ticket_id,
            status=target_status_str,
            owner_type=target_owner_str,
            assigned_employee_id=update_data.assigned_employee_id,
            queue_name=update_data.queue_name,
            status_notes=update_data.status_notes,
            assigned_at=datetime.utcnow()
        )
        
        self.ticket_repo.save_history(new_history_entry)
        self.ticket_repo.commit()

        self.index_ticket_data(update_data, ticket)

        return self.ticket_repo.refresh(ticket)

    def index_ticket_data(self, update_data: StatusHistoryCreateRequest, ticket: TicketModel) -> None:
        """
        Structures and syncs a resolved technical issue into the vector store.
        Uses decoupled metadata parameters for high-precision MCP filtering.
        """
        if update_data.status == TicketStatus.RESOLVED and self.vector_store:
            try:
                # Pair original symptoms with administrative fix action for optimized retrieval
                searchable_document = (
                    f"User Issue / Symptom: {ticket.ticket_description}\n"
                    f"Admin Resolution / Fix Action: {ticket.resolution_summary}"
                )

                # Keep attributes completely flat and separated to align with the new Pydantic schema
                metadata = {
                    "ticket_id": str(ticket.ticket_id),
                    "catalog_category": ticket.catalog_category,
                    "catalog_item": ticket.catalog_item,
                    "request_sub_type": ticket.request_sub_type or "None"
                }
                
                # Commit to the vectorized knowledge base
                self.vector_store.add_texts(
                    texts=[searchable_document],
                    metadatas=[metadata]
                )
                logger.info(f"Successfully vectorized and indexed resolved ticket #{ticket.ticket_id}")

            except Exception as vector_error:
                # Failsafe: Ensures a problem with your Vector DB network doesn't roll back the Postgres state
                logger.error(f"PostgreSQL committed successfully, but background vector store indexing failed: {vector_error}")