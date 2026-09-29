from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from controllers.utils import get_db
from controllers.token_verifier import verify_token
from controllers.auth_controller import register_user, login_user
from controllers.user_controller import (
    get_current_user_profile,
    update_user_profile,
    get_user_by_id,
)
from models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    TokenResponse,
)

router = APIRouter()


# ==========================================
# Health
# ==========================================
@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok", "service": "bazaar-users"}


# ==========================================
# Authentication Endpoints
# ==========================================
@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. The implementation goes in controllers/auth_controller.py."""
    return register_user(user_data, db)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
)
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate user. The implementation goes in controllers/auth_controller.py."""
    return login_user(login_data, db)


# ==========================================
# User Profile Endpoints (Protected)
# ==========================================
@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def get_me(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """Fetch current user profile. The implementation goes in controllers/user_controller.py."""
    return get_current_user_profile(user_id, db)


@router.put(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
def update_me(
    update_data: UserUpdateRequest,
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Update current user profile. The implementation goes in controllers/user_controller.py."""
    return update_user_profile(user_id, update_data, db)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch public user profile. The implementation goes in controllers/user_controller.py."""
    return get_user_by_id(user_id, db)
