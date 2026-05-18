# src/modules/__init__.py
from src.modules.core.database import Base
from src.modules.employees.models import EmployeeModel
from src.modules.tickets.models import TicketModel, TicketStatusHistoryModel

__all__ = ["Base", "EmployeeModel", "TicketModel", "TicketStatusHistoryModel"]