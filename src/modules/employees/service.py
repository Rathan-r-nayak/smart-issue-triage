from src.modules.employees.repository import EmployeeRepository
from src.modules.employees.schemas import EmployeeCreate
from src.modules.employees.models import EmployeeModel
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    def register_employee(self, employee_in: EmployeeCreate) -> EmployeeModel:
        logger.info(f"Attempting to register employee: {employee_in.email}")
        # Check if already exists
        existing = self.repository.get_by_id(employee_in.employee_id)
        if existing:
            logger.warning(f"Registration failed: Employee ID {employee_in.employee_id} already exists")
            raise ValueError("Employee ID already registered")

        new_employee = EmployeeModel(**employee_in.model_dump())
        result = self.repository.create(new_employee)
        logger.info(f"Successfully registered employee: {result.employee_id}")
        return result

    def fetch_profile(self, employee_id: str) -> EmployeeModel:
        logger.info(f"Fetching profile for employee: {employee_id}")
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            logger.error(f"Profile not found for employee: {employee_id}")
            raise ValueError("Employee profile not found")
        return employee