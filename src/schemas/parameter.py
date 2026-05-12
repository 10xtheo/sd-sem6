from typing import Optional
from pydantic import BaseModel, ConfigDict


class ParameterBase(BaseModel):
    short_name: str
    name: str
    param_type_code: str
    enum_type_id: Optional[int] = None
    unit_id: Optional[int] = None


class ParameterCreate(ParameterBase):
    pass


class ParameterUpdate(BaseModel):
    short_name: Optional[str] = None
    name: Optional[str] = None
    enum_type_id: Optional[int] = None
    unit_id: Optional[int] = None


class ParameterOut(BaseModel):
    id: int
    short_name: str
    name: str

    param_type_id: int   # ← просто поле, НЕ computed
    enum_type_id: Optional[int] = None
    unit_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)