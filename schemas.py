from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import List, Optional

# Base schema for employee data
class EmployeeBase(BaseModel):
    employee_id: str = Field(..., description="Unique ID for the employee")
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    department: str

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    class Config:
        from_attributes = True

# Schema for attendance marking
class AttendanceBase(BaseModel):
    date: date
    status: str = Field(..., pattern="^(Present|Absent)$")

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    employee_id: str

    class Config:
        from_attributes = True

# Aggregated data for dashboard/summary
class AttendanceSummary(BaseModel):
    total_records: int
    present_days: int
    absent_days: int

class DashboardSummary(BaseModel):
    total_employees: int
    total_departments: int
    present_today: int
    absent_today: int
    recent_employees: List[Employee]
    department_counts: dict
