from typing import List, Optional
from sqlalchemy.orm import Session

from repository.enum_repository import EnumRepository
from models.enum_type import EnumType
from models.enum_value import EnumValue


class EnumService:
    def __init__(self, session: Session):
        self.repo = EnumRepository(session)

    def get_all_types(self) -> List[EnumType]:
        return self.repo.get_enum_types()

    def get_type(self, type_id: int) -> EnumType:
        obj = self.repo.get_enum_type(type_id)
        if not obj:
            raise ValueError(f"Тип перечисления {type_id} не найден")
        return obj

    def create_type(self, data: dict) -> EnumType:
        return self.repo.create_enum_type(data)

    def update_type(self, type_id: int, data: dict) -> EnumType:
        obj = self.repo.update_enum_type(type_id, data)
        if not obj:
            raise ValueError(f"Тип перечисления {type_id} не найден")
        return obj

    def delete_type(self, type_id: int) -> None:
        if not self.repo.delete_enum_type(type_id):
            raise ValueError(f"Тип перечисления {type_id} не найден")

    def get_values_by_type(self, type_id: int, desc: bool = False) -> List[EnumValue]:
        return self.repo.get_enum_values_by_type(type_id, desc)

    def get_all_values(self) -> List[EnumValue]:
        return self.repo.get_enum_values()

    def get_value(self, value_id: int) -> EnumValue:
        obj = self.repo.get_enum_value(value_id)
        if not obj:
            raise ValueError(f"Значение перечисления {value_id} не найдено")
        return obj

    def create_value(self, data: dict) -> EnumValue:
        return self.repo.create_enum_value(data)

    def update_value(self, value_id: int, data: dict) -> EnumValue:
        obj = self.repo.update_enum_value(value_id, data)
        if not obj:
            raise ValueError(f"Значение перечисления {value_id} не найдено")
        return obj

    def delete_value(self, value_id: int) -> None:
        if not self.repo.delete_enum_value(value_id):
            raise ValueError(f"Значение перечисления {value_id} не найдено")

    def validate(self, type_code: str, value: str) -> EnumValue:
        return self.repo.validate_value_in_type(type_code, value)
