from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from src.modules.core.database import Base

class EmployeeModel(Base):
    __tablename__ = "employees"

    employee_id = Column(String(50), primary_key=True, index=True)
    employee_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(15), nullable=False)
    department_group = Column(String(50), server_default="Internal Support")
    default_location = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to tickets
    tickets = relationship("TicketModel", back_populates="employee")