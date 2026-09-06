from typing import Optional

from pydantic import BaseModel


class CustomerIn(BaseModel):
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    customer_group: str = "normal"


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    customer_group: Optional[str] = None


class CustomerOut(CustomerIn):
    id: int

    model_config = {"from_attributes": True}
