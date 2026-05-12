from typing import Optional
from pydantic import BaseModel, ConfigDict

from schemas.parameter import ParameterOut

class CategoryParameterBase(BaseModel):
    order_num: int = 0
    min_val: Optional[float] = None
    max_val: Optional[float] = None


class CategoryParameterCreate(CategoryParameterBase):
    category_id: int
    parameter_id: int


class CategoryParameterOut(CategoryParameterBase):
    category_id: int
    parameter_id: int
    parameter: Optional[ParameterOut] = None  # можно подгружать

    model_config = ConfigDict(from_attributes=True)
