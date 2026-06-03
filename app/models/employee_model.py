from sqlalchemy import (
    Column, Integer, String, Float, Date,
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.database import Base


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    PROBATION = "probation"


class Department(str, enum.Enum):
    ENGINEERING = "Engineering"
    HR = "Human Resources"
    FINANCE = "Finance"
    MARKETING = "Marketing"
    OPERATIONS = "Operations"
    SALES = "Sales"
    LEGAL = "Legal"
    IT = "IT"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    department = Column(Enum(Department), nullable=False)
    designation = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False)
    date_of_joining = Column(Date, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    status = Column(
        Enum(EmploymentStatus),
        default=EmploymentStatus.ACTIVE,
        nullable=False
    )

    # Foreign key to User (one-to-one)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    user = relationship("User", back_populates="employee")

    # Self-referential: manager relationship
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    manager = relationship("Employee", remote_side=[id], back_populates="subordinates")
    subordinates = relationship("Employee", back_populates="manager")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee id={self.id} code={self.employee_code} name={self.full_name}>"
