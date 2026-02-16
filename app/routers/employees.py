from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models.employee import Employee, EmployeeStatus
from app.models.department import Department
from app.schemas.employee import (
    EmployeeCreate, 
    EmployeeUpdate, 
    EmployeeResponse,
    EmployeeWithDepartment
)
from app.core.dependencies import (
    get_current_user, 
    get_admin_user, 
    get_hr_or_admin_user
)
from app.models.user import User
from app.services.audit_service import create_audit_log, AuditAction
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/employees", tags=["Employees"])


# CREATE - Add new employee
@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_or_admin_user)
):
    # check if employee_id already exists
    existing_emp_id = db.query(Employee).filter(Employee.employee_id == employee_data.employee_id).first()
    if existing_emp_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID '{employee_data.employee_id}' already exists"
        )
    
    # check if email already exists
    existing_email = db.query(Employee).filter(Employee.email == employee_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # check if department exists
    department = db.query(Department).filter(Department.id == employee_data.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id {employee_data.department_id} not found"
        )
    
    # create employee
    new_employee = Employee(**employee_data.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    create_audit_log(
        db=db,
        user=current_user,
        action=AuditAction.CREATE_EMPLOYEE,
        entity_type="employee",
        entity_id=new_employee.id,
        details={
            "employee_id": new_employee.employee_id,
            "name": f"{new_employee.first_name} {new_employee.last_name}",
            "email": new_employee.email
        }
    )
    
    return new_employee


# GET ALL - List employees with pagination
@router.get("/", response_model=List[EmployeeResponse])
def get_all_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    status: Optional[EmployeeStatus] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Employee)
    
    # Apply filters if provided
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if status:
        query = query.filter(Employee.status == status)
    if location:
        query = query.filter(Employee.location.ilike(f"%{location}%"))
    
    employees = query.offset(skip).limit(limit).all()
    return employees

# GET by Employee ID (business identifier like "EMP001")
@router.get("/by-emp-id/{employee_id}", response_model=EmployeeWithDepartment)
def get_employee_by_emp_id(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with employee_id '{employee_id}' not found"
        )
    
    response = EmployeeWithDepartment.model_validate(employee)
    response.department_name = employee.department.name
    
    return response

# GET using ID - get single employee by ID
@router.get("/{employee_id}", response_model=EmployeeWithDepartment)
def get_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # create response with department name
    response = EmployeeWithDepartment.model_validate(employee)
    response.department_name = employee.department.name
    
    return response


# UPDATE - update employee
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_or_admin_user)
):
    employee = db.query(Employee).filter(Employee.id == id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # get only the fields that were actually provided (not None)
    update_data = employee_data.model_dump(exclude_unset=True)
     # Store old values for audit log
    old_values = {field: getattr(employee, field) for field in update_data.keys()}   
    # If email is being updated, check its not already taken
    if "email" in update_data:
        existing = db.query(Employee).filter(
            Employee.email == update_data["email"],
            Employee.id != id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # If department_id is being updated, check it exists
    if "department_id" in update_data:
        department = db.query(Department).filter(Department.id == update_data["department_id"]).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with id {update_data['department_id']} not found"
            )
    
    # Update only provided fields
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    create_audit_log(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE_EMPLOYEE,
        entity_type="employee",
        entity_id=employee.id,
        details={
            "changed_fields": list(update_data.keys()),
            "old_values": {k: str(v) for k, v in old_values.items()},
            "new_values": {k: str(v) for k, v in update_data.items()}
        }
    )
    return employee


# DELETE - Remove employee
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    employee = db.query(Employee).filter(Employee.id == id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    employee_info = {
        "employee_id": employee.employee_id,
        "name": f"{employee.first_name} {employee.last_name}",
        "email": employee.email
    }
    db.delete(employee)
    db.commit()
    # Need to create new log since employee is deleted
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.DELETE_EMPLOYEE,
        entity_type="employee",
        entity_id=id,
        details=employee_info
    )
    db.add(audit_log)
    db.commit()
    return None  # 204 No Content

