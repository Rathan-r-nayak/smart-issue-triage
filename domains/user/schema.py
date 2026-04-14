from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    id: str = Field(..., description= "The unique ID from Identity Provider")
    email: EmailStr = Field(...)
    full_name : str = Field(..., min_length=2)
    role: str = Field("developer")


class UserResponse(UserCreate):
    created_at: datetime
    model_config = ConfigDict(from_attributes= True)