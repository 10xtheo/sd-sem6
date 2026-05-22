from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from schemas.parameter import ParameterValue


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


class PositionFull(BaseModel):
    """Position with all parameter values — used by the search endpoint."""
    id: int
    category_id: int
    name: str
    parameters: List[ParameterValue] = []

    model_config = ConfigDict(from_attributes=True)
