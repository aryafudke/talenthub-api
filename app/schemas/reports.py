from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

# Summary Report
class SummaryReport(BaseModel):
    total_employees: int
    total_departments: int
    active_employees: int
    inactive_employees: int
    on_leave_employees: int
    average_salary: Optional[float] = None


# Department Stats
class DepartmentStats(BaseModel):
    department_id: int
    department_name: str
    employee_count: int
    average_salary: Optional[float] = None
    total_salary: Optional[float] = None


class DepartmentStatsReport(BaseModel):
    total_departments: int
    stats: List[DepartmentStats]


# Salary Stats
class SalaryStats(BaseModel):
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    average_salary: Optional[float] = None
    total_salary: Optional[float] = None
    employee_count: int


# Hiring Trends
class HiringTrend(BaseModel):
    year: int
    month: int
    month_name: str
    employees_hired: int


class HiringTrendsReport(BaseModel):
    total_hires: int
    trends: List[HiringTrend]