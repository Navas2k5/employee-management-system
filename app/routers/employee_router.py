from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.employee_service import EmployeeService
from app.schemas.employee_schema import (
    EmployeeCreateRequest, EmployeeUpdateRequest,
    EmployeeResponse, PaginatedEmployeeResponse
)
from app.models.employee_model import Department, EmploymentStatus
from app.models.user_model import User
from app.dependencies.auth import (
    get_current_user,
    require_admin_or_hr,
    require_admin_hr_or_manager,
)

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee (Admin / HR)",
)
def create_employee(
    payload: EmployeeCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    """
    Create a new employee record. Requires **Admin** or **HR** role.
    - Auto-generates a unique employee code (e.g. EMP0001)
    - Optionally link to an existing user account via `user_id`
    - Optionally assign a manager via `manager_id`
    """
    return EmployeeService(db).create_employee(payload)


@router.get(
    "/",
    response_model=PaginatedEmployeeResponse,
    summary="List employees with pagination & filtering",
)
def list_employees(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Records per page"),
    department: Optional[Department] = Query(default=None, description="Filter by department"),
    status: Optional[EmploymentStatus] = Query(default=None, description="Filter by status"),
    search: Optional[str] = Query(default=None, description="Search by name, email, or code"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Retrieve a paginated list of employees. All authenticated users can access this.
    Supports filtering by **department**, **status**, and full-text **search**.
    """
    return EmployeeService(db).list_employees(
        page=page,
        page_size=page_size,
        department=department,
        status=status,
        search=search,
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get a single employee by ID",
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Fetch full details of a specific employee by their ID."""
    return EmployeeService(db).get_employee(employee_id)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update employee details (Admin / HR / Manager)",
)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_hr_or_manager),
):
    """
    Update employee information. Requires **Admin**, **HR**, or **Manager** role.
    Only fields provided in the request body will be updated (partial update).
    """
    return EmployeeService(db).update_employee(employee_id, payload)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an employee (Admin only)",
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_or_hr),
):
    """Permanently delete an employee record. Requires **Admin** or **HR** role."""
    return EmployeeService(db).delete_employee(employee_id)


@router.get(
    "/{manager_id}/subordinates",
    response_model=List[EmployeeResponse],
    summary="Get all subordinates of a manager",
)
def get_subordinates(
    manager_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieve all direct reports for a given manager ID."""
    return EmployeeService(db).get_subordinates(manager_id)
