from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from models.category import Category
from models.position import Position



class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        """Добавление новой категории"""
        category = Category(name=name, parent_id=parent_id)
        self.session.add(category)
        self.session.commit()
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        """Получение категории по ID"""
        return Category.get_by_id(self.session, category_id)

    def get_all_categories(self) -> List[Category]:
        """Получение всех категорий"""
        return Category.get_all(self.session)

    def move_category(self, category_id: int, new_parent_id: Optional[int]) -> Category:
        """Перемещение категории"""
        category = self.get_category(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена")

        # Проверка на циклы
        if new_parent_id:
            # Проверяем, не пытаемся ли мы сделать категорию родителем самой себя
            if category_id == new_parent_id:
                raise ValueError("Категория не может быть родителем самой себя")
            
            # Проверяем, не является ли новый родитель потомком текущей категории
            parent = self.get_category(new_parent_id)
            if parent:
                # Простая проверка на цикл (можно усложнить при необходимости)
                current = parent
                while current:
                    if current.id == category_id:
                        raise ValueError("Операция создаст цикл в иерархии")
                    current = current.parent

        category.parent_id = new_parent_id
        self.session.commit()
        return category

    def delete_category(self, category_id: int, cascade: bool = False) -> None:
        """Удаление категории"""
        category = self.get_category(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена")

        # Проверка наличия потомков
        children = category.get_children(self.session)
        if children and not cascade:
            children_ids = [c.id for c in children]
            raise ValueError(
                f"Категория имеет потомков: {children_ids}. "
                "Используйте cascade=True для каскадного удаления"
            )

        self.session.delete(category)
        self.session.commit()

    def get_category_tree(self) -> List[Dict[str, Any]]:
        """Получение дерева категорий"""
        def build_tree(parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
            categories = self.session.execute(
                select(Category).where(Category.parent_id == parent_id).order_by(Category.id)
            ).scalars().all()
            
            result = []
            for cat in categories:
                positions = Position.get_by_category(self.session, cat.id)
                result.append({
                    "id": cat.id,
                    "name": cat.name,
                    "children": build_tree(cat.id),
                    "positions": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "weight": p.weight,
                            "calories": p.calories,
                            "protein": p.protein,
                            "fat": p.fat,
                            "carbs": p.carbs,
                            "is_liquid": p.is_liquid,
                            "is_hot": p.is_hot
                        }
                        for p in positions
                    ]
                })
            return result
        
        return build_tree()
