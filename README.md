# 🏢 Employee Management System API

A production-ready **Employee Management System** built with **FastAPI**, featuring JWT authentication, Role-Based Access Control (RBAC), SQLAlchemy ORM with MySQL, full CRUD operations, and paginated filtering.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 |
| Database | MySQL (via PyMySQL) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## 📁 Project Structure

```
employee-management-system/
│
├── app/
│   ├── main.py                  # App entry point, middleware, router registration
│   │
│   ├── core/
│   │   ├── config.py            # Pydantic Settings (reads from .env)
│   │   └── security.py          # JWT creation/decoding, password hashing
│   │
│   ├── database/
│   │   └── database.py          # SQLAlchemy engine, session, Base, get_db()
│   │
│   ├── models/
│   │   ├── user_model.py        # User model with role enum
│   │   └── employee_model.py    # Employee model with self-referential manager FK
│   │
│   ├── schemas/
│   │   ├── auth_schema.py       # Register / Login / Token / Profile schemas
│   │   └── employee_schema.py   # Create / Update / Response / Paginated schemas
│   │
│   ├── routers/
│   │   ├── auth_router.py       # /api/v1/auth/* endpoints
│   │   └── employee_router.py   # /api/v1/employees/* endpoints
│   │
│   ├── services/
│   │   ├── auth_service.py      # Business logic for auth
│   │   └── employee_service.py  # Business logic for employees
│   │
│   ├── repository/
│   │   ├── auth_repository.py   # DB queries for User model
│   │   └── employee_repository.py # DB queries for Employee model
│   │
│   └── dependencies/
│       └── auth.py              # get_current_user, require_roles(), RBAC helpers
│
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone / Extract the project

```bash
cd employee-management-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit `.env` with your MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=employee_management

SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Create the MySQL database

```sql
CREATE DATABASE employee_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Tables are auto-created on first startup via SQLAlchemy `create_all`.

---

## 📖 API Documentation

Once running, visit:
- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## 🔐 Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/v1/auth/register` | Public | Register new user |
| POST | `/api/v1/auth/login` | Public | Login, get JWT |
| GET | `/api/v1/auth/me` | All roles | Get own profile |
| PUT | `/api/v1/auth/change-password` | All roles | Change password |
| PATCH | `/api/v1/auth/deactivate/{id}` | Admin | Deactivate user |

---

## 👥 Employee Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/v1/employees/` | Admin, HR | Create employee |
| GET | `/api/v1/employees/` | All roles | List with pagination & filters |
| GET | `/api/v1/employees/{id}` | All roles | Get employee by ID |
| PUT | `/api/v1/employees/{id}` | Admin, HR, Manager | Update employee |
| DELETE | `/api/v1/employees/{id}` | Admin, HR | Delete employee |
| GET | `/api/v1/employees/{id}/subordinates` | All roles | Get direct reports |

---

## 🔑 Roles & Permissions

| Role | Permissions |
|------|-------------|
| `admin` | Full access — all endpoints |
| `hr` | Create, read, update, delete employees |
| `manager` | Read all + update employees |
| `employee` | Read-only access |

---

## 🔍 Filtering & Pagination

The `GET /api/v1/employees/` endpoint supports:

```
GET /api/v1/employees/?page=1&page_size=10&department=Engineering&status=active&search=john
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Records per page (1–100, default: 10) |
| `department` | enum | Filter by department |
| `status` | enum | Filter by employment status |
| `search` | string | Search name, email, code, designation |

**Response:**
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "data": [...]
}
```

---

## 🗃️ Data Models

### User Roles
`admin` | `hr` | `manager` | `employee`

### Departments
`Engineering` | `Human Resources` | `Finance` | `Marketing` | `Operations` | `Sales` | `Legal` | `IT`

### Employment Status
`active` | `on_leave` | `terminated` | `probation`

---

## 🔗 SQLAlchemy Relationships

- **User ↔ Employee**: One-to-one (a user account can be linked to one employee)
- **Employee ↔ Employee**: Self-referential many-to-one (manager → subordinates)

---

## 📝 Quick Start Example

```bash
# 1. Register an admin user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@company.com","password":"Admin1234","role":"admin"}'

# 2. Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin1234"}'

# 3. Create an employee (use token from step 2)
curl -X POST http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@company.com",
    "department": "Engineering",
    "designation": "Software Engineer",
    "salary": 85000,
    "date_of_joining": "2024-01-15"
  }'
```

---

## 🏗️ Architecture Pattern

This project follows a **layered architecture**:

```
Router → Service → Repository → Database
```

- **Router**: HTTP layer, request/response handling
- **Service**: Business logic, validation, error handling
- **Repository**: Database abstraction, all raw queries live here
- **Models**: SQLAlchemy ORM table definitions
- **Schemas**: Pydantic request/response validation

---

## 🔒 Security Best Practices Implemented

- Passwords hashed with **bcrypt** (never stored in plain text)
- JWT tokens with configurable expiry
- Role-based route protection via dependency injection
- Input validation via Pydantic v2 with custom validators
- Environment variables for all secrets (never hardcoded)
