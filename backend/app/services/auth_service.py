"""Authentication and user management service."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    """Service handling user registration, authentication and JWT generation."""

    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        """Register a new user account with hashed password and assigned role."""
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise ValueError(f"Email {user_in.email} đã được sử dụng!")

        # Find role by code, default to customer
        role_code = user_in.role_code or "customer"
        role = db.query(Role).filter(Role.code == role_code).first()
        if not role:
            # Fallback to first available role or create default customer role
            role = db.query(Role).filter(Role.code == "customer").first()
            if not role:
                role = Role(code="customer", name="Khách hàng", description="Người dùng mua hàng")
                db.add(role)
                db.flush()

        user = User(
            role_id=role.id,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            phone=user_in.phone,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user credentials and return the User entity."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Email hoặc mật khẩu không chính xác!")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Email hoặc mật khẩu không chính xác!")

        if not user.is_active:
            raise ValueError("Tài khoản của bạn đã bị khóa hoặc chưa được kích hoạt!")

        return user

    @staticmethod
    def create_token_for_user(user: User) -> str:
        """Generate JWT access token for user."""
        return create_access_token(subject=str(user.id))
