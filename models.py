from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

# Employee model for storing staff details
class Employee(Base):
    __tablename__ = "employees"

    # Unique employee identifier (provided by admin)
    employee_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)

    # Relationship to attendance records
    attendance = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

# Attendance model for daily tracking
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False) # Present / Absent

    # Link back to employee
    employee = relationship("Employee", back_populates="attendance")

    # Prevent duplicate attendance for same employee on same date
    __table_args__ = (UniqueConstraint('employee_id', 'date', name='_employee_date_uc'),)
