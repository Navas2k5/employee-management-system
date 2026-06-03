from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    UserRegisterRequest, UserLoginRequest,
    TokenResponse, UserResponse, ChangePasswordRequest
)
from app.dependencies.auth import get_current_user, require_admin
from app.models.user_model import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    - **username**: unique, 3–50 characters
    - **email**: valid email address
    - **password**: minimum 8 characters
    - **role**: admin | hr | manager | employee (default: employee)
    """
    return AuthService(db).register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain JWT token",
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive a Bearer token for subsequent requests."""
    return AuthService(db).login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_profile(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


@router.put(
    "/change-password",
    summary="Change current user password",
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the password of the currently authenticated user."""
    return AuthService(db).change_password(current_user.id, payload)


@router.patch(
    "/deactivate/{user_id}",
    summary="Deactivate a user account (Admin only)",
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Deactivate a user account. Requires Admin role."""
    return AuthService(db).deactivate_user(user_id)
