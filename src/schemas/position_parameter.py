from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from schemas.position import PositionOut
from schemas.parameter import ParameterValue


class PositionWithParameters(BaseModel):
    """Полная позиция со всеми её параметрами"""
    position: PositionOut
    position_parameters: List[ParameterValue] = []

    model_config = ConfigDict(from_attributes=True)

class PositionWithAllParameters(PositionWithParameters):
    category_parameters: List[ParameterValue] = []
