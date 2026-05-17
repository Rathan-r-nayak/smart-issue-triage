from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from src.modules.core.database import Base
from src.modules.tickets.constants import TicketStatus, AssigneeOwner

class TicketModel(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    specific_facility = Column(String(100), nullable=False)
    catalog_category = Column(String(50), nullable=False)
    catalog_item = Column(String(50), nullable=False)
    request_sub_type = Column(String(100), nullable=True)
    ticket_description = Column(Text, nullable=False)
    callback_consent = Column(Boolean, server_default="TRUE")
    resolution_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("EmployeeModel", back_populates="tickets")
    status_history = relationship("TicketStatusHistoryModel", back_populates="ticket", cascade="all, delete-orphan")


class TicketStatusHistoryModel(Base):
    __tablename__ = "ticket_status_history"

    status_entry_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)
    
    # Using Enums at the database level for strict data integrity
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.DRAFT)
    assigned_owner = Column(SQLEnum(AssigneeOwner), nullable=False, default=AssigneeOwner.AI_AGENT)
    
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status_notes = Column(Text, nullable=True)

    # Relationship back to the core ticket
    ticket = relationship("TicketModel", back_populates="status_history")