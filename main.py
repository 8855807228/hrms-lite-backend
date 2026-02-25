from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import models, schemas, crud
from database import engine, get_db

# Initialize database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HRMS Lite API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard", response_model=schemas.DashboardSummary)
def read_dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)

@app.get("/api/employees", response_model=List[schemas.Employee])
def read_employees(db: Session = Depends(get_db)):
    return crud.get_employees(db)

@app.post("/api/employees", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check for duplicate employee ID
    db_employee = db.query(models.Employee).filter(models.Employee.employee_id == employee.employee_id).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Check for duplicate email
    db_email = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    return crud.create_employee(db=db, employee=employee)

@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    success = crud.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

@app.get("/api/employees/{employee_id}/attendance", response_model=List[schemas.Attendance])
def read_attendance(
    employee_id: str, 
    date_from: Optional[date] = None, 
    date_to: Optional[date] = None, 
    db: Session = Depends(get_db)
):
    return crud.get_attendance(db, employee_id, date_from, date_to)

@app.get("/api/employees/{employee_id}/attendance/summary", response_model=schemas.AttendanceSummary)
def read_attendance_summary(employee_id: str, db: Session = Depends(get_db)):
    return crud.get_attendance_summary(db, employee_id)

@app.post("/api/employees/{employee_id}/attendance", response_model=schemas.Attendance)
def mark_attendance(employee_id: str, attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    # Ensure employee exists
    db_employee = db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return crud.mark_attendance(db, employee_id, attendance)
