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


class PositionParameterValue(BaseModel):
    parameter_id: int
    short_name: str
    name: str
    type_code: str
    type_name: str
    unit_symbol: Optional[str] = None

    val_real: Optional[float] = None
    val_int: Optional[int] = None
    val_str: Optional[str] = None
    val_dt: Optional[str] = None
    enum_val_id: Optional[int] = None
    enum_val_name: Optional[str] = None


class PositionWithParameters(BaseModel):
    position: PositionOut
    parameters: List[PositionParameterValue]

    model_config = ConfigDict(from_attributes=True)
