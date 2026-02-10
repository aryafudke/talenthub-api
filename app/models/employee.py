from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.connection import Base


# status options 
class EmployeeStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"


# employee model
class Employee(Base):
    __tablename__ = "employees"
    
    # primary Key - auto-generated unique ID
    id = Column(Integer, primary_key=True, index=True)
    
    # EMP001"
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # personal Info
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    
    # department - foreign key 
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    
    # job Info
    designation = Column(String(100), nullable=False) 
    salary = Column(Numeric(12, 2), nullable=False)
    hire_date = Column(Date, nullable=False)
    location = Column(String(100), nullable=False)
    
    # status
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.active, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # relationship - allows employee.department to get full department object
    department = relationship("Department", back_populates="employees")