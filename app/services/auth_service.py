from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repository.auth_repository import AuthRepository
from app.schemas.auth_schema import (
    UserRegisterRequest, UserLoginRequest,
    TokenResponse, UserResponse, ChangePasswordRequest
)
from app.models.user_model import User
from app.core.security import (
    verify_password, get_password_hash, create_access_token
)


class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def register(self, payload: UserRegisterRequest) -> UserResponse:
        # Check username uniqueness
        if self.repo.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{payload.username}' is already taken."
            )
        # Check email uniqueness
        if self.repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{payload.email}' is already registered."
            )

        user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            role=payload.role,
        )
        created = self.repo.create(user)
        return UserResponse.model_validate(created)

    def login(self, payload: UserLoginRequest) -> TokenResponse:
        user = self.repo.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Contact your administrator."
            )

        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        return TokenResponse(
            access_token=token,
            role=user.role,
            username=user.username,
        )

    def get_profile(self, user_id: int) -> UserResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return UserResponse.model_validate(user)

    def change_password(
        self, user_id: int, payload: ChangePasswordRequest
    ) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )
        user.hashed_password = get_password_hash(payload.new_password)
        self.repo.update(user)
        return {"message": "Password changed successfully."}

    def deactivate_user(self, user_id: int) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        user.is_active = False
        self.repo.update(user)
        return {"message": f"User '{user.username}' has been deactivated."}
