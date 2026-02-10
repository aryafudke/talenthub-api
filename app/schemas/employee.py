from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# status
class EmployeeStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"


# Base schema 
class EmployeeBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=20, examples=["EMP001"])
    first_name: str = Field(..., min_length=1, max_length=50, examples=["Arya"])
    last_name: str = Field(..., min_length=1, max_length=50, examples=["Fudke"])
    email: EmailStr = Field(..., examples=["aryafudke@gmail.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+91-9876543210"])
    department_id: int = Field(..., gt=0, examples=[1])
    designation: str = Field(..., min_length=1, max_length=100, examples=["Software Engineer"])
    salary: Decimal = Field(..., gt=0, examples=[1500000.00])
    hire_date: date = Field(..., examples=["2024-01-15"])
    location: str = Field(..., min_length=1, max_length=100, examples=["Mumbai"])
    status: EmployeeStatus = Field(default=EmployeeStatus.active)


# create employee (request body)
class EmployeeCreate(EmployeeBase):
    pass # same as base


# updating employee fields
class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = Field(None, gt=0)
    designation: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[Decimal] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[EmployeeStatus] = None

# responses
class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  


# response with department name included
class EmployeeWithDepartment(EmployeeResponse):
    department_name: Optional[str] = None