from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, text

from models.position import Position
from models.category import Category
from models.position_parameter import PositionParameter
from models.parameter import Parameter
from repository.position_parameter_repository import PositionParameterRepository


class PositionRepository:
    def __init__(self, session: Session):
        self.session = session
        self.param_repo = PositionParameterRepository(session)

    # ====================== БАЗОВЫЙ CRUD ======================

    def add_position(
        self,
        category_id: int,
        name: str,
    ) -> Position:
        """Создание позиции (только базовые поля)"""
        category = self.session.get(Category, category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена")

        position = Position(
            category_id=category_id,
            name=name,
        )
        self.session.add(position)
        self.session.commit()
        self.session.refresh(position)
        return position

    def get_position(self, position_id: int) -> Optional[Position]:
        return self.session.get(Position, position_id)

    def get_positions_by_category(self, category_id: int) -> List[Position]:
        return list(self.session.execute(
            select(Position)
            .where(Position.category_id == category_id)
            .order_by(Position.id)
        ).scalars().all())

    def get_all_positions(self) -> List[Position]:
        return list(self.session.execute(select(Position)).scalars().all())

    def update_position(self, position_id: int, name: Optional[str] = None) -> Position:
        """Обновление только базовых полей позиции"""
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        if name is not None:
            position.name = name

        self.session.commit()
        self.session.refresh(position)
        return position

    def delete_position(self, position_id: int) -> None:
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        self.session.delete(position)
        self.session.commit()

    def move_position(self, position_id: int, new_category_id: int) -> Position:
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        category = self.session.get(Category, new_category_id)
        if not category:
            raise ValueError(f"Категория с ID {new_category_id} не найдена")

        position.category_id = new_category_id
        self.session.commit()
        return position

    # ====================== ПОИСК И ФИЛЬТРАЦИЯ ======================

    def search_positions(self, query: str) -> List[Position]:
        return list(self.session.execute(
            select(Position).where(Position.name.ilike(f"%{query}%"))
        ).scalars().all())

    def get_filtered_positions(
        self,
        category_id: Optional[int] = None,
        # Дополнительные фильтры по параметрам можно добавить позже
    ) -> List[Position]:
        stmt = select(Position)

        if category_id is not None:
            stmt = stmt.where(Position.category_id == category_id)

        return list(self.session.execute(stmt.order_by(Position.id)).scalars().all())

    # ====================== РАБОТА С ПАРАМЕТРАМИ ======================

    def write_parameter(
        self,
        position_id: int,
        parameter_id: int,
        val_real: Optional[float] = None,
        val_int: Optional[int] = None,
        val_str: Optional[str] = None,
        val_dt: Optional[str] = None,
        enum_val_id: Optional[int] = None,
    ) -> None:
        """Запись значения параметра (аналог write_par_position)"""
        self.param_repo.write_value(
            position_id=position_id,
            parameter_id=parameter_id,
            val_real=val_real,
            val_int=val_int,
            val_str=val_str,
            val_dt=val_dt,
            enum_val_id=enum_val_id,
        )

    def get_position_full(self, position_id: int):
        position = self.get_position(position_id)
        if not position:
            return None

        parameters = self.session.execute(
            select(PositionParameter)
            .where(PositionParameter.position_id == position_id)
        ).scalars().all()

        return position, parameters

    def get_position_with_parameters(self, position_id: int):
        """Альтернативный метод с загрузкой через ORM"""
        position = self.session.query(Position).options(
            joinedload(Position.parameters).joinedload(PositionParameter.parameter)
        ).filter(Position.id == position_id).first()

        return position

    # ====================== СЛУЖЕБНЫЕ ======================

    def delete_all(self) -> int:
        try:
            # Удаляем сначала значения параметров
            self.session.execute(text("DELETE FROM position_parameters"))
            deleted_count = self.session.query(Position).delete()
            self.session.commit()
            return deleted_count
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ошибка при удалении позиций: {str(e)}")

    def get_position_parents(self, position: Position) -> List[Category]:
        parents = []
        current = position.category
        while current:
            parents.append(current)
            current = current.parent
        return parents
    
    def set_enum_value(self, position_id: int, parameter_id: int, enum_val_id: int):
        """Установить значение enum-параметра"""
        self.param_repo.write_value(
            position_id=position_id,
            parameter_id=parameter_id,
            enum_val_id=enum_val_id
        )
