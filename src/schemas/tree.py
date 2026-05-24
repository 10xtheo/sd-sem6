from typing import List, Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field


class TreeParamValue(BaseModel):
    parameter_id: int
    short_name: Optional[str] = None
    name: Optional[str] = None
    val_real: Optional[float] = None
    val_int: Optional[int] = None
    val_str: Optional[str] = None
    val_dt: Optional[str] = None
    enum_val_id: Optional[int] = None


class TreeCategory(BaseModel):
    type: Literal["category"] = "category"
    id: int
    name: str
    level: int
    parent_id: Optional[int] = None


class TreePosition(BaseModel):
    type: Literal["position"] = "position"
    id: int
    name: str
    category_id: int
    level: int
    parameters: List[TreeParamValue] = []


TreeItem = Annotated[Union[TreeCategory, TreePosition], Field(discriminator="type")]


class TreeResponse(BaseModel):
    items: List[TreeItem] = []


class TreeFilter(BaseModel):
    short_name: str
    min: Optional[float] = None
    max: Optional[float] = None
    eq: Optional[str] = None
    contains: Optional[str] = None
