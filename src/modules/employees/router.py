from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.core.database import get_db
from src.modules.employees.schemas import EmployeeCreate, EmployeeResponse
from src.modules.employees.repository import EmployeeRepository
from src.modules.employees.service import EmployeeService
from src.modules.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    repo = EmployeeRepository(db)
    return EmployeeService(repo)



@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee_in: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)):
    logger.info(f"Received request to create employee: {employee_in.email}")
    try:
        employee = service.register_employee(employee_in)
        logger.info(f"Successfully created employee: {employee.employee_id}")
        return employee
    except ValueError as e:
        logger.error(f"Error creating employee: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, service: EmployeeService = Depends(get_employee_service)):
    logger.info(f"Received request to fetch employee profile: {employee_id}")
    try:
        employee = service.fetch_profile(employee_id)
        logger.info(f"Successfully fetched employee profile: {employee_id}")
        return employee
    except ValueError as e:
        logger.error(f"Employee profile not found: {employee_id}")
        raise HTTPException(status_code=404, detail=str(e))