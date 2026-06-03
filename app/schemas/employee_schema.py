from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date, datetime
from app.models.employee_model import EmploymentStatus, Department


class EmployeeCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Department
    designation: str
    salary: float
    date_of_joining: date
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    manager_id: Optional[int] = None
    user_id: Optional[int] = None

    @field_validator("salary")
    @classmethod
    def salary_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Salary must be a positive value")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name fields must not be empty")
        return v


class EmployeeUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[Department] = None
    designation: Optional[str] = None
    salary: Optional[float] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    status: Optional[EmploymentStatus] = None
    manager_id: Optional[int] = None

    @field_validator("salary")
    @classmethod
    def salary_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Salary must be a positive value")
        return v


class ManagerBriefResponse(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    designation: str

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    department: Department
    designation: str
    salary: float
    date_of_joining: date
    date_of_birth: Optional[date]
    address: Optional[str]
    status: EmploymentStatus
    manager: Optional[ManagerBriefResponse] = None
    user_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaginatedEmployeeResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[EmployeeResponse]
