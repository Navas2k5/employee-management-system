from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import Optional, List, Tuple
from app.models.employee_model import Employee, Department, EmploymentStatus


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        return (
            self.db.query(Employee)
            .options(joinedload(Employee.manager))
            .filter(Employee.id == employee_id)
            .first()
        )

    def get_by_code(self, employee_code: str) -> Optional[Employee]:
        return (
            self.db.query(Employee)
            .filter(Employee.employee_code == employee_code)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.email == email).first()

    def get_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        department: Optional[Department] = None,
        status: Optional[EmploymentStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        query = self.db.query(Employee).options(joinedload(Employee.manager))

        # Filter by department
        if department:
            query = query.filter(Employee.department == department)

        # Filter by status
        if status:
            query = query.filter(Employee.status == status)

        # Search by name, email, or employee code
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.email.ilike(search_term),
                    Employee.employee_code.ilike(search_term),
                    Employee.designation.ilike(search_term),
                )
            )

        total = query.count()
        employees = (
            query.order_by(Employee.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return employees, total

    def get_by_manager(self, manager_id: int) -> List[Employee]:
        return (
            self.db.query(Employee)
            .filter(Employee.manager_id == manager_id)
            .all()
        )

    def generate_employee_code(self) -> str:
        """Auto-generate unique employee code like EMP0001."""
        last = (
            self.db.query(Employee)
            .order_by(Employee.id.desc())
            .first()
        )
        next_id = (last.id + 1) if last else 1
        return f"EMP{next_id:04d}"

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def update(self, employee: Employee) -> Employee:
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.commit()
