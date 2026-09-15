"""FastAPI dependencies module (DB session, JWT auth & RBAC permissions)."""

from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# OAuth2 scheme for Swagger UI & Authorization header extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Optional[User]:
    """Retrieve authenticated user if valid token is provided, otherwise return None."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user if (user and user.is_active) else None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Enforce authenticated user token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực tài khoản (Token không tồn tại)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa",
        )
    return user


def require_role(allowed_roles: List[str]) -> Callable:
    """Dependency factory checking if current user has an allowed role."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.code if current_user.role else ""
        if user_role not in allowed_roles and "admin" not in user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Quyền truy cập bị từ chối. Yêu cầu một trong các vai trò: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


__all__ = ["get_db", "get_current_user", "get_current_user_optional", "require_role"]
