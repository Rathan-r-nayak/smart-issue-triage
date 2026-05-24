from typing import List

from sqlalchemy.orm import Session
from src.modules.employees.models import EmployeeModel
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: str) -> EmployeeModel:
        logger.info(f"Fetching employee by ID: {employee_id}")
        return self.db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()

    def create(self, employee: EmployeeModel) -> EmployeeModel:
        logger.info(f"Creating new employee: {employee.email}")
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        logger.info(f"Successfully created employee with ID: {employee.employee_id}")
        return employee
    
    def get_all(self) -> List[EmployeeModel]:
        """Fetch all registered employees from the database."""
        return self.db.query(EmployeeModel).all()