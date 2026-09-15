"""Pydantic schemas export module."""

from app.schemas.role import RoleBase, RoleCreate, RoleOut
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserOut,
    Token,
    TokenPayload,
)
from app.schemas.category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryOut,
)
from app.schemas.store import StoreBase, StoreCreate, StoreUpdate, StoreOut
from app.schemas.product import ProductBase, ProductCreate, ProductUpdate, ProductOut
from app.schemas.batch import (
    BatchBase,
    BatchCreate,
    BatchUpdate,
    BatchDiscountUpdate,
    BatchOut,
    BatchExpiringOut,
)
from app.schemas.ai_recommendation import (
    AIRecommendationBase,
    AIRecommendationCreate,
    AIRecommendationApproval,
    AIRecommendationOut,
)
from app.schemas.order import (
    OrderItemBase,
    OrderItemCreate,
    OrderItemOut,
    OrderCreate,
    OrderUpdateStatus,
    OrderOut,
)
from app.schemas.payment import (
    PaymentBase,
    PaymentCreate,
    PaymentUpdateStatus,
    PaymentOut,
)
from app.schemas.ai import AIDiscountRequest, AIDiscountResponse

__all__ = [
    "RoleBase",
    "RoleCreate",
    "RoleOut",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserOut",
    "Token",
    "TokenPayload",
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryOut",
    "StoreBase",
    "StoreCreate",
    "StoreUpdate",
    "StoreOut",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductOut",
    "BatchBase",
    "BatchCreate",
    "BatchUpdate",
    "BatchDiscountUpdate",
    "BatchOut",
    "BatchExpiringOut",
    "AIRecommendationBase",
    "AIRecommendationCreate",
    "AIRecommendationApproval",
    "AIRecommendationOut",
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemOut",
    "OrderCreate",
    "OrderUpdateStatus",
    "OrderOut",
    "PaymentBase",
    "PaymentCreate",
    "PaymentUpdateStatus",
    "PaymentOut",
    "AIDiscountRequest",
    "AIDiscountResponse",
]
