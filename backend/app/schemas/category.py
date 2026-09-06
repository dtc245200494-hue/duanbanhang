from typing import Optional

from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str
    description: str = ""


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}
