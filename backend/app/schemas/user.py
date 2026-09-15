"""User and Authentication Pydantic v2 schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""

    email: str = Field(..., max_length=150, description="Email đăng nhập")
    full_name: str = Field(..., max_length=100, description="Họ và tên đầy đủ")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại")


class UserCreate(UserBase):
    """Schema for registering a new user."""

    password: str = Field(..., min_length=6, description="Mật khẩu tài khoản")
    role_code: Optional[str] = Field("customer", description="Mã vai trò: admin, store_manager, customer")


class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: str
    password: str


class UserOut(UserBase):
    """Schema for returning user profile."""

    id: int
    role_id: int
    role_code: Optional[str] = None
    role_name: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for returning JWT access token."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    """Schema representing decoded JWT payload."""

    sub: Optional[str] = None
