"""Unit tests for Authentication, JWT tokens, and RBAC."""

import pytest
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.core.security import verify_password, decode_access_token


def test_user_registration_and_password_hashing(db_session):
    """Test user registration hashes password and assigns default role."""
    user_in = UserCreate(
        email="newuser@example.com",
        full_name="Nguyễn Người Dùng Mới",
        phone="0912345678",
        password="MySecretPassword123",
        role_code="customer",
    )

    user = AuthService.register_user(db=db_session, user_in=user_in)

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.hashed_password != "MySecretPassword123"
    assert verify_password("MySecretPassword123", user.hashed_password) is True
    assert user.role.code == "customer"


def test_user_authentication_success_and_jwt(db_session):
    """Test authentication generates valid JWT token."""
    user = AuthService.authenticate_user(
        db=db_session, email="customer@freshmart.vn", password="Admin@123"
    )
    assert user is not None
    assert user.email == "customer@freshmart.vn"

    token = AuthService.create_token_for_user(user)
    assert token is not None
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user.id)


def test_user_authentication_wrong_password(db_session):
    """Test authentication raises error on wrong password."""
    with pytest.raises(ValueError) as exc:
        AuthService.authenticate_user(
            db=db_session, email="customer@freshmart.vn", password="WrongPassword"
        )
    assert "không chính xác" in str(exc.value)
