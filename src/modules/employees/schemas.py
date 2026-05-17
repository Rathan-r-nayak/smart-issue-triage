from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class EmployeeCreate(BaseModel):
    employee_id: str
    employee_name: str
    email: EmailStr
    phone_number: str
    department_group: Optional[str] = "Internal Support"
    default_location: str

class EmployeeResponse(EmployeeCreate):
    created_at: datetime

    class Config:
        from_attributes = True