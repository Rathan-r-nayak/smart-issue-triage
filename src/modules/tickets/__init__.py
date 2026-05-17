# models/__init__.py
from src.modules.core.database import Base
from .employee_model import Employee
from .ticket_model import Ticket
from .status_history_model import TicketStatusHistory

# Expose Base so main.py can trigger a clean engine table build easily
__all__ = ["Base", "Employee", "Ticket", "TicketStatusHistory"]