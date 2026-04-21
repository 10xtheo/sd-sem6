from pydantic import BaseModel

class EnumValidateIn(BaseModel):
    type_code: str
    value: str