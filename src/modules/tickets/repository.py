from typing import List

from sqlalchemy.orm import Session
from src.modules.tickets.models import CatalogMasterModel, TicketModel, TicketStatusHistoryModel

class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_ticket(self, ticket: TicketModel) -> TicketModel:
        self.db.add(ticket)
        self.db.flush()  # Populates new_ticket.ticket_id automatically via Postgres
        return ticket

    def save_history(self, history: TicketStatusHistoryModel) -> TicketStatusHistoryModel:
        self.db.add(history)
        self.db.flush()
        return history

    def commit(self):
        self.db.commit()

    def refresh(self, instance):
        self.db.refresh(instance)
        return instance
    

    def get_by_id(self, ticket_id: int) -> TicketModel:
        """Fetch a specific ticket by its primary key."""
        return self.db.query(TicketModel).filter(TicketModel.ticket_id == ticket_id).first()

    def get_all(self) -> List[TicketModel]:
        """Fetch all tickets ordered by creation time descending."""
        return self.db.query(TicketModel).order_by(TicketModel.created_at.desc()).all()
    
    def get_all_catalog_items(self) -> List[CatalogMasterModel]:
        """Fetch all consistent catalog lookup rules stored in the master table."""
        return self.db.query(CatalogMasterModel).all()