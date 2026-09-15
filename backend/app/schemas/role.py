"""Role Pydantic v2 schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    """Base schema for role definition."""

    code: str = Field(..., max_length=50, description="Mã vai trò: admin, store_manager, customer")
    name: str = Field(..., max_length=100, description="Tên hiển thị vai trò")
    description: Optional[str] = Field(None, description="Mô tả chi tiết quyền hạn")


class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    pass


class RoleOut(RoleBase):
    """Schema for returning role details."""

    id: int

    model_config = ConfigDict(from_attributes=True)
