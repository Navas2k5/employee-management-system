import math
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repository.employee_repository import EmployeeRepository
from app.schemas.employee_schema import (
    EmployeeCreateRequest, EmployeeUpdateRequest,
    EmployeeResponse, PaginatedEmployeeResponse
)
from app.models.employee_model import Employee, Department, EmploymentStatus


class EmployeeService:
    def __init__(self, db: Session):
        self.repo = EmployeeRepository(db)

    def create_employee(self, payload: EmployeeCreateRequest) -> EmployeeResponse:
        # Check email uniqueness
        if self.repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email '{payload.email}' already exists."
            )

        # Validate manager exists
        if payload.manager_id:
            manager = self.repo.get_by_id(payload.manager_id)
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Manager with id {payload.manager_id} not found."
                )

        employee = Employee(
            employee_code=self.repo.generate_employee_code(),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            department=payload.department,
            designation=payload.designation,
            salary=payload.salary,
            date_of_joining=payload.date_of_joining,
            date_of_birth=payload.date_of_birth,
            address=payload.address,
            manager_id=payload.manager_id,
            user_id=payload.user_id,
        )
        created = self.repo.create(employee)
        # Reload with manager relation
        return EmployeeResponse.model_validate(self.repo.get_by_id(created.id))

    def get_employee(self, employee_id: int) -> EmployeeResponse:
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )
        return EmployeeResponse.model_validate(employee)

    def list_employees(
        self,
        page: int = 1,
        page_size: int = 10,
        department: Optional[Department] = None,
        status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None,
    ) -> PaginatedEmployeeResponse:
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be >= 1."
            )
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 100."
            )

        employees, total = self.repo.get_all_paginated(
            page=page,
            page_size=page_size,
            department=department,
            status=status,
            search=search,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return PaginatedEmployeeResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=[EmployeeResponse.model_validate(e) for e in employees],
        )

    def update_employee(
        self, employee_id: int, payload: EmployeeUpdateRequest
    ) -> EmployeeResponse:
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )

        # Validate manager
        if payload.manager_id is not None:
            if payload.manager_id == employee_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An employee cannot be their own manager."
                )
            manager = self.repo.get_by_id(payload.manager_id)
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Manager with id {payload.manager_id} not found."
                )

        # Apply updates
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        updated = self.repo.update(employee)
        return EmployeeResponse.model_validate(self.repo.get_by_id(updated.id))

    def delete_employee(self, employee_id: int) -> dict:
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found."
            )
        # Unassign subordinates before deleting
        for sub in employee.subordinates:
            sub.manager_id = None

        self.repo.delete(employee)
        return {"message": f"Employee '{employee.full_name}' deleted successfully."}

    def get_subordinates(self, manager_id: int):
        manager = self.repo.get_by_id(manager_id)
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manager with id {manager_id} not found."
            )
        subordinates = self.repo.get_by_manager(manager_id)
        return [EmployeeResponse.model_validate(e) for e in subordinates]
