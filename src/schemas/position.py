from typing import Optional
from pydantic import BaseModel


class PositionCreate(BaseModel):
    category_id: int
    name: str
    weight: Optional[int] = None
    weight_unit_id: Optional[int] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    fat: Optional[int] = None
    carbs: Optional[int] = None
    is_liquid: bool = False
    is_hot: bool = False


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    weight_unit_id: Optional[int] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    fat: Optional[int] = None
    carbs: Optional[int] = None
    is_liquid: Optional[bool] = None
    is_hot: Optional[bool] = None


class PositionMove(BaseModel):
    new_category_id: int


class PositionOut(BaseModel):
    id: int
    category_id: int
    name: str
    weight: Optional[int] = None
    weight_unit_id: Optional[int] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    fat: Optional[int] = None
    carbs: Optional[int] = None
    is_liquid: bool
    is_hot: bool

    model_config = {"from_attributes": True}
