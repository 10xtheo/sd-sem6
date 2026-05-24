from typing import Optional, List
from sqlalchemy.orm import Session

from repository.position_repository import PositionRepository
from repository.position_parameter_repository import PositionParameterRepository
from models.enum_value import EnumValue


class PositionParameterService:
    def __init__(self, session: Session):
        self.session = session
        self.position_repo = PositionRepository(session)
        self.repo = PositionParameterRepository(session)

    def write(
        self,
        position_id: int,
        parameter_id: int,
        val_real: Optional[float] = None,
        val_int: Optional[int] = None,
        val_str: Optional[str] = None,
        val_dt: Optional[str] = None,
        enum_val_id: Optional[int] = None,
    ) -> None:
        position = self.position_repo.get(position_id)
        if not position:
            raise ValueError(f"Позиция {position_id} не найдена")

        bounds = self.repo.get_param_with_bounds(parameter_id, position.category_id)
        if not bounds:
            raise ValueError(
                f"Параметр {parameter_id} не привязан к категории позиции {position_id}"
            )

        param, min_val, max_val = bounds
        type_code = param.param_type.code if param.param_type else None
        if not type_code:
            raise ValueError(f"Не удалось определить тип параметра {parameter_id}")

        self._validate(type_code, min_val, max_val, val_real, val_int, val_str, val_dt, enum_val_id, param)
        self.repo.upsert(position_id, parameter_id, val_real, val_int, val_str, val_dt, enum_val_id)

    def _validate(
        self,
        type_code: str,
        min_val: Optional[float],
        max_val: Optional[float],
        val_real: Optional[float],
        val_int: Optional[int],
        val_str: Optional[str],
        val_dt: Optional[str],
        enum_val_id: Optional[int],
        param,
    ) -> None:
        if type_code == "real":
            if val_real is None:
                raise ValueError('Для параметра типа "real" требуется val_real')
            if val_real < 0:
                raise ValueError("Отрицательное значение недопустимо для val_real")
            if min_val is not None and val_real < min_val:
                raise ValueError(f"Значение {val_real} меньше допустимого минимума {min_val}")
            if max_val is not None and val_real > max_val:
                raise ValueError(f"Значение {val_real} больше допустимого максимума {max_val}")

        elif type_code == "integer":
            if val_int is None:
                raise ValueError('Для параметра типа "integer" требуется val_int')
            if val_int < 0:
                raise ValueError("Отрицательное значение недопустимо для val_int")
            if min_val is not None and val_int < min_val:
                raise ValueError(f"Значение {val_int} меньше допустимого минимума {min_val}")
            if max_val is not None and val_int > max_val:
                raise ValueError(f"Значение {val_int} больше допустимого максимума {max_val}")

        elif type_code == "string":
            if not val_str or not val_str.strip():
                raise ValueError('Для параметра типа "string" требуется val_str')

        elif type_code == "datetime":
            if val_dt is None:
                raise ValueError('Для параметра типа "datetime" требуется val_dt')

        elif type_code == "enum":
            if enum_val_id is None:
                raise ValueError('Для параметра типа "enum" требуется enum_val_id')
            if not self._enum_value_belongs_to_type(enum_val_id, param.enum_type_id):
                raise ValueError(
                    f"Значение enum_val_id={enum_val_id} не принадлежит к указанному перечислению"
                )
        else:
            raise ValueError(f'Неизвестный тип параметра: "{type_code}"')

    def _enum_value_belongs_to_type(self, enum_val_id: int, enum_type_id: Optional[int]) -> bool:
        if not enum_type_id:
            return False
        return (
            self.session.query(EnumValue)
            .filter(EnumValue.id == enum_val_id, EnumValue.enum_type_id == enum_type_id)
            .first()
        ) is not None

    def get_for_position(self, position_id: int):
        position = self.position_repo.get(position_id)
        if not position:
            raise ValueError(f"Позиция {position_id} не найдена")
        return self.repo.get_for_position(position_id)

    def delete(self, position_id: int, parameter_id: int) -> None:
        deleted = self.repo.delete(position_id, parameter_id)
        if not deleted:
            raise ValueError(
                f"Параметр {parameter_id} для позиции {position_id} не найден"
            )
