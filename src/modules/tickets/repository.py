from typing import List, Optional
from sqlalchemy.orm import Session
from src.modules.tickets.models import CatalogMasterModel, TicketModel, TicketStatusHistoryModel
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_ticket(self, ticket: TicketModel) -> TicketModel:
        logger.info("Saving new ticket to database")
        self.db.add(ticket)
        self.db.flush()  # Populates new_ticket.ticket_id automatically via Postgres
        logger.info(f"Ticket flushed with ID: {ticket.ticket_id}")
        return ticket

    def save_history(self, history: TicketStatusHistoryModel) -> TicketStatusHistoryModel:
        logger.info(f"Saving status history for ticket: {history.ticket_id}")
        self.db.add(history)
        self.db.flush()
        return history

    def commit(self):
        logger.debug("Committing transaction")
        self.db.commit()

    def refresh(self, instance):
        self.db.refresh(instance)
        return instance


    def get_by_id(self, ticket_id: int) -> TicketModel:
        """Fetch a specific ticket by its primary key."""
        logger.info(f"Fetching ticket by ID: {ticket_id}")
        return self.db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    def get_all(self) -> List[TicketModel]:
        """Fetch all tickets ordered by creation time descending."""
        logger.info("Fetching all tickets from database")
        return self.db.query(TicketModel).order_by(TicketModel.created_at.desc()).all()

    def get_all_catalog_items(self) -> List[CatalogMasterModel]:
        """Fetch all consistent catalog lookup rules stored in the master table."""
        logger.info("Fetching all catalog items")
        return self.db.query(CatalogMasterModel).all()
    

    def get_by_id(self, ticket_id: int) -> Optional[TicketModel]:
        """Fetch a specific ticket and its full nested status history by ID."""
        return self.db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    def search_tickets(self, employee_id: Optional[str] = None, description_query: Optional[str] = None) -> List[TicketModel]:
        """
        Dynamically filter tickets by employee_id, fuzzy text query on description, or both.
        """
        query = self.db.query(TicketModel)
        
        if employee_id:
            query = query.filter(TicketModel.employee_id == employee_id)
            
        if description_query:
            # Performs a case-insensitive fuzzy match: %query%
            query = query.filter(TicketModel.ticket_description.ilike(f"%{description_query}%"))
            
        return query.order_by(TicketModel.created_at.desc()).all()