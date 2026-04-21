from pydantic import BaseModel, ConfigDict


class EnumTypeBase(BaseModel):
    name: str
    code: str


class EnumTypeCreate(EnumTypeBase):
    pass


class EnumTypeUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class EnumTypeOut(EnumTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
