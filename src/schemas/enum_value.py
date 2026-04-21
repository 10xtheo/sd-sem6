from pydantic import BaseModel, ConfigDict


class EnumValueBase(BaseModel):
    enum_type_id: int
    order_number: int
    name: str
    code: str | None = None
    numeric_value: float | None = None
    unit_id: int | None = None


class EnumValueCreate(EnumValueBase):
    pass


class EnumValueUpdate(BaseModel):
    order_number: int | None = None
    name: str | None = None
    code: str | None = None
    numeric_value: float | None = None
    unit_id: int | None = None


class EnumValueOut(EnumValueBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
