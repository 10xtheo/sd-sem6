from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ====================== БАЗОВЫЕ СХЕМЫ ======================

class PositionOutMinimal(BaseModel):
    """Базовая информация о позиции (используется внутри PositionWithParameters)"""
    id: int
    category_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PositionParameterValueBase(BaseModel):
    """Базовые поля одного параметра"""
    parameter_id: int
    short_name: str
    name: str
    type_code: str
    type_name: Optional[str] = None
    unit_symbol: Optional[str] = None


class PositionParameterValue(PositionParameterValueBase):
    """Полное значение параметра позиции"""
    val_real: Optional[float] = None
    val_int: Optional[int] = None
    val_str: Optional[str] = None
    val_dt: Optional[str] = None
    enum_val_id: Optional[int] = None
    enum_val_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ====================== КОМПОЗИТНАЯ СХЕМА ======================

class PositionWithParameters(BaseModel):
    """Полная позиция со всеми её параметрами"""
    position: PositionOutMinimal
    parameters: List[PositionParameterValue] = []

    model_config = ConfigDict(from_attributes=True)
