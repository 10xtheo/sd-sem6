from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from models.category import Category
from models.position import Position


class PositionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_position(
        self,
        category_id: int,
        name: str,
        weight: Optional[int] = None,
        calories: Optional[int] = None,
        protein: Optional[int] = None,
        fat: Optional[int] = None,
        carbs: Optional[int] = None,
        is_liquid: bool = False,
        is_hot: bool = False
    ) -> Position:
        """Добавление новой позиции"""
        category = Category.get_by_id(self.session, category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена")

        position = Position(
            category_id=category_id,
            name=name,
            weight=weight,
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs,
            is_liquid=is_liquid,
            is_hot=is_hot
        )
        self.session.add(position)
        self.session.commit()
        return position

    def get_position(self, position_id: int) -> Optional[Position]:
        """Получение позиции по ID"""
        return Position.get_by_id(self.session, position_id)

    def get_positions_by_category(self, category_id: int) -> List[Position]:
        """Получение всех позиций категории"""
        return Position.get_by_category(self.session, category_id)

    def get_all_positions(self) -> List[Position]:
        """Получение всех позиций"""
        return Position.get_all(self.session)

    def update_position(self, position_id: int, **kwargs) -> Position:
        """Обновление позиции"""
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        for key, value in kwargs.items():
            if hasattr(position, key) and value is not None:
                setattr(position, key, value)

        self.session.commit()
        return position

    def delete_position(self, position_id: int) -> None:
        """Удаление позиции"""
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        self.session.delete(position)
        self.session.commit()

    def move_position(self, position_id: int, new_category_id: int) -> Position:
        """Перемещение позиции в другую категорию"""
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Позиция с ID {position_id} не найдена")

        category = Category.get_by_id(self.session, new_category_id)
        if not category:
            raise ValueError(f"Категория с ID {new_category_id} не найдена")

        position.category_id = new_category_id
        self.session.commit()
        return position

    def search_positions(self, query: str) -> List[Position]:
        """Поиск позиций по названию"""
        return Position.search_by_name(self.session, query)

    def get_filtered_positions(
        self,
        min_calories: Optional[int] = None,
        max_calories: Optional[int] = None,
        is_liquid: Optional[bool] = None,
        is_hot: Optional[bool] = None,
        category_id: Optional[int] = None
    ) -> List[Position]:
        """Получение позиций с фильтрацией"""
        filters = []
        
        if min_calories is not None:
            filters.append(Position.calories >= min_calories)
        if max_calories is not None:
            filters.append(Position.calories <= max_calories)
        if is_liquid is not None:
            filters.append(Position.is_liquid == is_liquid)
        if is_hot is not None:
            filters.append(Position.is_hot == is_hot)
        if category_id is not None:
            filters.append(Position.category_id == category_id)

        stmt = select(Position)
        if filters:
            stmt = stmt.where(and_(*filters))
        
        return list(self.session.execute(stmt.order_by(Position.id)).scalars().all())

    def delete_all(self) -> int:
            """Удаление всех позиций"""
            try:
                deleted_count = self.session.query(Position).delete()
                self.session.commit()
                return deleted_count
            except Exception as e:
                self.session.rollback()
                raise Exception(f"Ошибка при удалении позиций: {str(e)}")

    def get_position_parents(self, position):
        parents = []
        current = position.category

        while current:
            parents.append(current)
            current = current.parent

        return parents
    
    def get_positions_tree(self, category, level=0):
        result = [("category", category, level)]

        # позиции этой категории
        positions = Position.get_by_category(self.session, category.id)
        for pos in positions:
            result.append(("position", pos, level + 1))

        # подкатегории
        children = (
            self.session.query(Category)
            .filter(Category.parent_id == category.id)
            .order_by(Category.id)
            .all()
        )

        for child in children:
            result.extend(self.get_positions_tree(child, level + 1))

        return result
