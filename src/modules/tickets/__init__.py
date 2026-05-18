# models/__init__.py
from src.modules.core.database import Base
from .models import Employee
from .models import Ticket
from .models import TicketStatusHistory

# Expose Base so main.py can trigger a clean engine table build easily
__all__ = ["Base", "Employee", "Ticket", "TicketStatusHistory"]