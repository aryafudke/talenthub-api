from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.core.dependencies import get_current_user

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department

# POST create department
@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept_data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # check if department name already exists
    existing = db.query(Department).filter(Department.name == dept_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists"
        )
    
    new_department = Department(
        name=dept_data.name,
        description=dept_data.description
    )
    
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    
    return new_department

# PUT update department
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, dept_data: DepartmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # update only provided fields
    if dept_data.name is not None:
        # check if new name conflicts with existing
        existing = db.query(Department).filter(Department.name == dept_data.name, Department.id != department_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists"
            )
        department.name = dept_data.name
    
    if dept_data.description is not None:
        department.description = dept_data.description
    
    db.commit()
    db.refresh(department)
    
    return department

# DELETE department
@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    db.delete(department)
    db.commit()
    
    return None