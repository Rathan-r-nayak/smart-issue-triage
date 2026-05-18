from src.modules.employees.repository import EmployeeRepository
from src.modules.employees.schemas import EmployeeCreate
from src.modules.employees.models import EmployeeModel

class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    def register_employee(self, employee_in: EmployeeCreate) -> EmployeeModel:
        # Check if already exists
        existing = self.repository.get_by_id(employee_in.employee_id)
        if existing:
            raise ValueError("Employee ID already registered")
        
        new_employee = EmployeeModel(**employee_in.model_dump())
        return self.repository.create(new_employee)

    def fetch_profile(self, employee_id: str) -> EmployeeModel:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise ValueError("Employee profile not found")
        return employee