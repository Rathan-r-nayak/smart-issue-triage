from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.core.database import get_db
from src.modules.employees.schemas import EmployeeCreate, EmployeeResponse
from src.modules.employees.repository import EmployeeRepository
from src.modules.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    repo = EmployeeRepository(db)
    return EmployeeService(repo)



@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee_in: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)):
    try:
        return service.register_employee(employee_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, service: EmployeeService = Depends(get_employee_service)):
    try:
        return service.fetch_profile(employee_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))