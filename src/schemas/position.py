from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict


class PositionCreate(BaseModel):
    category_id: int
    name: str


class PositionUpdate(BaseModel):
    name: Optional[str] = None


class PositionMove(BaseModel):
    new_category_id: int


class PositionOut(BaseModel):
    id: int
    category_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
