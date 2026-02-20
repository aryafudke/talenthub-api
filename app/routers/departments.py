from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.core.dependencies import get_current_user, get_hr_or_admin_user, get_admin_user
from app.services.audit_service import create_audit_log, AuditAction
from app.core.exceptions import (
    DepartmentNotFoundException,
    DuplicateDepartmentNameException
)
router = APIRouter(prefix="/departments", tags=["Departments"])


#each endpoint [1. Query DB 2. check if exists 3. Return result]

# GET all departments
@router.get("/", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    departments = db.query(Department).all()
    return departments

# GET single department
@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise DepartmentNotFoundException(id)
    
    return department

# POST create department
@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept_data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    # check if department name already exists
    existing = db.query(Department).filter(Department.name == dept_data.name).first()
    if existing:
        raise DuplicateDepartmentNameException(dept_data.name)
    
    new_department = Department(
        name=dept_data.name,
        description=dept_data.description
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    create_audit_log(
        db=db,
        user=current_user,
        action=AuditAction.CREATE_EMPLOYEE,
        entity_type="employee",
        entity_id=new_department.id,
        details={
            "name": new_department.name,
            "description": new_department.description
        }
    )
    return new_department

# PUT update department
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    department = db.query(Department).filter(Department.id == id).first()
    if not department:
        raise DepartmentNotFoundException(id)
    
    update_data = department_data.model_dump(exclude_unset=True)
    
    # Store old values for audit
    old_values = {field: getattr(department, field) for field in update_data.keys()}
    
    # Check if new name conflicts
    if "name" in update_data:
        existing = db.query(Department).filter(
            Department.name == update_data["name"],
            Department.id != id
        ).first()
        if existing:
            raise DuplicateDepartmentNameException(update_data["name"])
    
    # Update fields
    for field, value in update_data.items():
        setattr(department, field, value)
    
    db.commit()
    db.refresh(department)
    
    # LOG THE ACTION
    create_audit_log(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE_DEPARTMENT,
        entity_type="department",
        entity_id=department.id,
        details={
            "changed_fields": list(update_data.keys()),
            "old_values": {k: str(v) for k, v in old_values.items()},
            "new_values": {k: str(v) for k, v in update_data.items()}
        }
    )
    
    return department

# DELETE department
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    department = db.query(Department).filter(Department.id == id).first()
    if not department:
        raise DepartmentNotFoundException(id)
    
    # Store info before deletion
    department_info = {
        "name": department.name,
        "description": department.description
    }
    department_id = department.id
    
    db.delete(department)
    db.commit()
    
    # LOG THE ACTION
    create_audit_log(
        db=db,
        user=current_user,
        action=AuditAction.DELETE_DEPARTMENT,
        entity_type="department",
        entity_id=department_id,
        details=department_info
    )
    
    return None


