from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from models.position_parameter import PositionParameter
from models.enum_value import EnumValue
from models.parameter import Parameter
from models.position import Position
from models.category_parameter import CategoryParameter

class PositionParameterRepository:
    def __init__(self, session: Session):
        self.session = session
    # Процедура WRITE_PAR_PROD бд TODO: отрефакторить вынести валидации в отдельную ф-цию
    def write_value(
        self,
        position_id: int,
        parameter_id: int,
        val_real: Optional[float] = None,
        val_int: Optional[int] = None,
        val_str: Optional[str] = None,
        val_dt: Optional[str] = None,
        enum_val_id: Optional[int] = None,
    ):
        """Универсальная запись значения параметра с полной валидацией (аналог write_par_position)"""

        # 1. Получаем категорию позиции
        position = self.session.get(Position, position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        category_id = position.category_id

        # 2. Получаем информацию о параметре + настройки категории
        stmt = (
            select(
                Parameter,
                CategoryParameter.order_num,
                CategoryParameter.min_val,
                CategoryParameter.max_val,
            )
            .join(CategoryParameter, CategoryParameter.parameter_id == Parameter.id)
            .where(
                CategoryParameter.category_id == category_id,
                Parameter.id == parameter_id
            )
        )

        result = self.session.execute(stmt).first()
        if not result:
            raise ValueError(
                f"Параметр {parameter_id} не привязан к категории позиции {position_id}"
            )

        parameter = result[0]
        min_val = result[2]
        max_val = result[3]

        # Получаем код типа параметра
        # parameter.param_type — это EnumValue (тип параметра: real/integer/...)
        type_code = parameter.param_type.code if parameter.param_type else None

        if not type_code:
            raise ValueError(f"Не удалось определить тип параметра {parameter_id}")

        # 3. Валидация по типу
        if type_code == 'real':
            if val_real is None:
                raise ValueError('Для параметра типа "real" требуется val_real')
            if min_val is not None and val_real < min_val:
                raise ValueError(f'Значение {val_real} меньше допустимого минимума {min_val}')
            if max_val is not None and val_real > max_val:
                raise ValueError(f'Значение {val_real} больше допустимого максимума {max_val}')

        elif type_code == 'integer':
            if val_int is None:
                raise ValueError('Для параметра типа "integer" требуется val_int')
            if min_val is not None and val_int < min_val:
                raise ValueError(f'Значение {val_int} меньше допустимого минимума {min_val}')
            if max_val is not None and val_int > max_val:
                raise ValueError(f'Значение {val_int} больше допустимого максимума {max_val}')

        elif type_code == 'string':
            if val_str is None or val_str.strip() == '':
                raise ValueError('Для параметра типа "string" требуется val_str')

        elif type_code == 'datetime':
            if val_dt is None:
                raise ValueError('Для параметра типа "datetime" требуется val_dt')

        elif type_code == 'enum':
            if enum_val_id is None:
                raise ValueError('Для параметра типа "enum" требуется enum_val_id')
            # Проверяем, что значение принадлежит нужному enum_type
            if not self._validate_enum_value(enum_val_id, parameter.enum_type_id):
                raise ValueError(
                    f"Значение enum_val_id={enum_val_id} не принадлежит "
                    f"к указанному перечислению параметра"
                )

        else:
            raise ValueError(f'Неизвестный тип параметра: "{type_code}"')

        # 4. Сохранение (upsert)
        pp = PositionParameter(
            position_id=position_id,
            parameter_id=parameter_id,
            val_real=val_real,
            val_int=val_int,
            val_str=val_str,
            val_dt=val_dt,
            enum_val_id=enum_val_id,
        )

        self.session.merge(pp)
        self.session.commit()

    def _validate_enum_value(self, enum_val_id: int, expected_enum_type_id: Optional[int]) -> bool:
        """Проверяет, что enum значение принадлежит нужному типу"""
        if expected_enum_type_id is None:
            return False

        exists = self.session.query(EnumValue).filter(
            EnumValue.id == enum_val_id,
            EnumValue.enum_type_id == expected_enum_type_id
        ).first()

        return exists is not None

    def get_for_position(self, position_id: int):
        position = self.session.get(Position, position_id)
        if not position:
            raise Exception(f"Position {position_id} not found")

        stmt = (
            select(Parameter)
            .outerjoin(
                CategoryParameter,
                CategoryParameter.parameter_id == Parameter.id
            )
            .outerjoin(
                PositionParameter,
                PositionParameter.parameter_id == Parameter.id
            )
            .where(
                or_(
                    CategoryParameter.category_id == position.category_id,
                    PositionParameter.position_id == position_id
                )
            )
            .distinct()
            .order_by(Parameter.short_name)
        )

        return self.session.scalars(stmt).all()
