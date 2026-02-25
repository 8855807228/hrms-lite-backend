from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models, schemas

# Fetch all employees
def get_employees(db: Session):
    return db.query(models.Employee).all()

# Create new employee
def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Delete employee and their records
def delete_employee(db: Session, employee_id: str):
    db_employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
    return db_employee

# Mark attendance (Update if exists, else Create)
def mark_attendance(db: Session, employee_id: str, attendance: schemas.AttendanceCreate):
    # Check if record already exists for this date
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.date == attendance.date
    ).first()
    
    if existing:
        existing.status = attendance.status
        db.commit()
        db.refresh(existing)
        return existing
    
    db_attendance = models.Attendance(**attendance.model_dump(), employee_id=employee_id)
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# Get attendance by employee with optional date range
def get_attendance(db: Session, employee_id: str, date_from: date = None, date_to: date = None):
    query = db.query(models.Attendance).filter(models.Attendance.employee_id == employee_id)
    if date_from:
        query = query.filter(models.Attendance.date >= date_from)
    if date_to:
        query = query.filter(models.Attendance.date <= date_to)
    return query.order_by(models.Attendance.date.desc()).all()

# Get summary for a specific employee
def get_attendance_summary(db: Session, employee_id: str):
    base_query = db.query(models.Attendance).filter(models.Attendance.employee_id == employee_id)
    total = base_query.count()
    present = base_query.filter(models.Attendance.status == "Present").count()
    absent = total - present
    return {"total_records": total, "present_days": present, "absent_days": absent}

# Dashboard data
def get_dashboard_summary(db: Session):
    today = date.today()
    total_emp = db.query(models.Employee).count()
    
    # Department breakdown
    dept_counts = db.query(models.Employee.department, func.count(models.Employee.employee_id)).group_by(models.Employee.department).all()
    dept_dict = {dept: count for dept, count in dept_counts}
    
    # Attendance for today
    present_today = db.query(models.Attendance).filter(models.Attendance.date == today, models.Attendance.status == "Present").count()
    absent_today = db.query(models.Attendance).filter(models.Attendance.date == today, models.Attendance.status == "Absent").count()
    
    # Recent employees (last 5)
    recent = db.query(models.Employee).limit(5).all()
    
    return {
        "total_employees": total_emp,
        "total_departments": len(dept_dict),
        "present_today": present_today,
        "absent_today": absent_today,
        "recent_employees": recent,
        "department_counts": dept_dict
    }
