"""Authentication and User management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.schemas.role import RoleOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """Register a new user account (Customer, Manager, or Admin)."""
    try:
        user = AuthService.register_user(db=db, user_in=user_in)
        return UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role_id=user.role_id,
            role_code=user.role.code if user.role else None,
            role_name=user.role.name if user.role else None,
            is_active=user.is_active,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )


@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Authenticate with email and password to receive a JWT access token."""
    try:
        user = AuthService.authenticate_user(
            db=db, email=login_in.email, password=login_in.password
        )
        token = AuthService.create_token_for_user(user)
        user_out = UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role_id=user.role_id,
            role_code=user.role.code if user.role else None,
            role_name=user.role.name if user.role else None,
            is_active=user.is_active,
        )
        return Token(access_token=token, token_type="bearer", user=user_out)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(val_err),
        )


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserOut:
    """Get the currently logged-in user profile."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role_id=current_user.role_id,
        role_code=current_user.role.code if current_user.role else None,
        role_name=current_user.role.name if current_user.role else None,
        is_active=current_user.is_active,
    )


@router.get("/roles", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db)) -> List[Role]:
    """List all available system roles."""
    return db.query(Role).all()


@router.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
) -> List[UserOut]:
    """List all users in the system (Admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            phone=u.phone,
            role_id=u.role_id,
            role_code=u.role.code if u.role else None,
            role_name=u.role.name if u.role else None,
            is_active=u.is_active,
        )
        for u in users
    ]
