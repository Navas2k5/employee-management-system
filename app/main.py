from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.database import create_tables
from app.routers import auth_router, employee_router

# Import models so SQLAlchemy registers them before create_all
from app.models import user_model, employee_model  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup: create DB tables if they don't exist."""
    create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-ready Employee Management System API built with FastAPI. "
        "Features include JWT authentication, role-based access control (RBAC), "
        "SQLAlchemy ORM with MySQL, full CRUD operations, and paginated filtering."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(employee_router.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
