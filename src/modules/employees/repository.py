from sqlalchemy.orm import Session
from src.modules.employees.models import EmployeeModel

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: str) -> EmployeeModel:
        return self.db.query(EmployeeModel).filter(EmployeeModel.employee_id == employee_id).first()

    def create(self, employee: EmployeeModel) -> EmployeeModel:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee