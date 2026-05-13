from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from schemas.enum_value import EnumValueOut
from schemas.enum_type import EnumTypeOut
from schemas.unit import UnitResponse

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
    
#=========================
    
class ParameterInfo(BaseModel):
    id: int
    short_name: str
    name: str
    paramType: EnumValueOut = Field(validation_alias="param_type")
    enumType: Optional[EnumTypeOut] = Field(default=None, validation_alias="enum_type")
    unit: Optional[UnitResponse] = None

    model_config = ConfigDict(from_attributes=True)
    
class ParameterValueBase(BaseModel):
    """Базовые поля одного параметра"""
    id: int
    short_name: str
    name: str
    paramType: EnumValueOut
    enumType: Optional[EnumTypeOut] = None
    unit: Optional[UnitResponse] = None


class ParameterValue(BaseModel):
    parameter: ParameterInfo

    val_real: Optional[float] = None
    val_int: Optional[int] = None
    val_str: Optional[str] = None
    val_dt: Optional[str] = None
    enum_value: Optional[EnumValueOut] = None

    model_config = ConfigDict(from_attributes=True)