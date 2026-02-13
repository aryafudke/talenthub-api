from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List

from app.database.connection import get_db
from app.models.employee import Employee, EmployeeStatus
from app.models.department import Department
from app.schemas.reports import (
    SummaryReport,
    DepartmentStats,
    DepartmentStatsReport,
    SalaryStats,
    HiringTrend,
    HiringTrendsReport
)
from app.core.dependencies import get_current_user, get_hr_or_admin_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


#  SUMMARY REPORT 
@router.get("/summary", response_model=SummaryReport)
def get_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall summary statistics.
    
    Returns total employees, departments, status breakdown, and average salary.
    """
    
    # Total employees
    total_employees = db.query(func.count(Employee.id)).scalar()
    
    # Total departments
    total_departments = db.query(func.count(Department.id)).scalar()
    
    # Count by status
    active_employees = db.query(func.count(Employee.id)).filter(
        Employee.status == EmployeeStatus.active
    ).scalar()
    
    inactive_employees = db.query(func.count(Employee.id)).filter(
        Employee.status == EmployeeStatus.inactive
    ).scalar()
    
    on_leave_employees = db.query(func.count(Employee.id)).filter(
        Employee.status == EmployeeStatus.on_leave
    ).scalar()
    
    # Average salary
    average_salary = db.query(func.avg(Employee.salary)).scalar()
    
    return SummaryReport(
        total_employees=total_employees or 0,
        total_departments=total_departments or 0,
        active_employees=active_employees or 0,
        inactive_employees=inactive_employees or 0,
        on_leave_employees=on_leave_employees or 0,
        average_salary=float(average_salary) if average_salary else None
    )


#  DEPARTMENT STATS 
@router.get("/department-stats", response_model=DepartmentStatsReport)
def get_department_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_or_admin_user)
):
    """
    Get employee statistics grouped by department.
    
    Returns employee count and salary stats per department.
    """
    
    # Query with GROUP BY
    stats = db.query(
        Department.id,
        Department.name,
        func.count(Employee.id).label("employee_count"),
        func.avg(Employee.salary).label("average_salary"),
        func.sum(Employee.salary).label("total_salary")
    ).outerjoin(
        Employee, Department.id == Employee.department_id
    ).group_by(
        Department.id, Department.name
    ).all()
    
    # Convert to response format
    department_stats = []
    for stat in stats:
        department_stats.append(DepartmentStats(
            department_id=stat.id,
            department_name=stat.name,
            employee_count=stat.employee_count or 0,
            average_salary=float(stat.average_salary) if stat.average_salary else None,
            total_salary=float(stat.total_salary) if stat.total_salary else None
        ))
    
    return DepartmentStatsReport(
        total_departments=len(department_stats),
        stats=department_stats
    )


#  SALARY STATS 
@router.get("/salary-stats", response_model=SalaryStats)
def get_salary_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_or_admin_user)
):
    """
    Get overall salary statistics.
    
    Returns min, max, average, and total salary.
    """
    
    # Get all salary stats in one query
    stats = db.query(
        func.min(Employee.salary).label("min_salary"),
        func.max(Employee.salary).label("max_salary"),
        func.avg(Employee.salary).label("average_salary"),
        func.sum(Employee.salary).label("total_salary"),
        func.count(Employee.id).label("employee_count")
    ).first()
    
    return SalaryStats(
        min_salary=float(stats.min_salary) if stats.min_salary else None,
        max_salary=float(stats.max_salary) if stats.max_salary else None,
        average_salary=float(stats.average_salary) if stats.average_salary else None,
        total_salary=float(stats.total_salary) if stats.total_salary else None,
        employee_count=stats.employee_count or 0
    )


#  HIRING TRENDS 
@router.get("/hiring-trends", response_model=HiringTrendsReport)
def get_hiring_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get hiring trends by month/year.
    
    Returns how many employees were hired each month.
    """
    
    # Month names for display
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    # Query with GROUP BY year and month
    trends = db.query(
        extract('year', Employee.hire_date).label("year"),
        extract('month', Employee.hire_date).label("month"),
        func.count(Employee.id).label("employees_hired")
    ).group_by(
        extract('year', Employee.hire_date),
        extract('month', Employee.hire_date)
    ).order_by(
        extract('year', Employee.hire_date).desc(),
        extract('month', Employee.hire_date).desc()
    ).all()
    
    # Convert to response format
    hiring_trends = []
    total_hires = 0
    
    for trend in trends:
        year = int(trend.year)
        month = int(trend.month)
        count = trend.employees_hired
        total_hires += count
        
        hiring_trends.append(HiringTrend(
            year=year,
            month=month,
            month_name=month_names[month],
            employees_hired=count
        ))
    
    return HiringTrendsReport(
        total_hires=total_hires,
        trends=hiring_trends
    )