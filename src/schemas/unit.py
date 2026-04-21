from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    code: str
    name: str
    symbol: str

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    symbol: str | None = None

class UnitResponse(UnitBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
