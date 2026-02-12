from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database.connection import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.employee import EmployeeResponse
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.llm_service import parse_search_query
from typing import List, Optional

router = APIRouter(prefix="/employees", tags=["Smart Search"])

# schema for smart search request
class SmartSearchRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "senior engineers in Mumbai earning above 15 LPA"
            }
        }

# schema for smart search response
class SmartSearchResponse(BaseModel):
    query: str # original query
    parsed_filters: dict # ai understanding
    results_count: int 
    results: List[EmployeeResponse]
    message: Optional[str] = None

@router.post("/smart-search", response_model=SmartSearchResponse)
def smart_search(
    request: SmartSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered natural language search for employees.
    
    Examples:
    - "engineers in Mumbai"
    - "senior developers earning above 20 LPA"
    - "employees hired after 2023"
    - "active employees in HR department"
    """
    
    # 1. parse natural language using Gemini
    parsed_filters = parse_search_query(request.query)
    
    if parsed_filters is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse search query. Please try again."
        )
    if not parsed_filters:  # Empty dict {}
        return SmartSearchResponse(
            query=request.query,
            parsed_filters=parsed_filters,
            results_count=0,
            results=[],
            message="No search criteria found. Try: 'engineers in Mumbai' or 'employees earning above 10 LPA'"
        )
    
    # 2: build SQLAlchemy query
    query = db.query(Employee)
    
    # apply filters based on parsed results
    if "designation" in parsed_filters:
        query = query.filter(Employee.designation.ilike(f"%{parsed_filters['designation']}%"))
    
    if "location" in parsed_filters:
        query = query.filter(Employee.location.ilike(f"%{parsed_filters['location']}%"))
    
    if "salary_min" in parsed_filters:
        query = query.filter(Employee.salary >= parsed_filters['salary_min'])
    
    if "salary_max" in parsed_filters:
        query = query.filter(Employee.salary <= parsed_filters['salary_max'])
    
    if "status" in parsed_filters:
        query = query.filter(Employee.status == parsed_filters['status'])
    
    if "hire_date_after" in parsed_filters:
        query = query.filter(Employee.hire_date >= parsed_filters['hire_date_after'])
    
    if "hire_date_before" in parsed_filters:
        query = query.filter(Employee.hire_date <= parsed_filters['hire_date_before'])
    
    # Handle department_name 
    if "department_name" in parsed_filters:
        query = query.join(Department).filter(
            Department.name.ilike(f"%{parsed_filters['department_name']}%")
        )
    
    # Step 3: Execute query
    employees = query.all()
    
    # Step 4: Return results with metadata
    return SmartSearchResponse(
        query=request.query,
        parsed_filters=parsed_filters,
        results_count=len(employees),
        results=employees
    )