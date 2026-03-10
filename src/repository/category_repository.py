from typing import List, Optional
from sqlalchemy.orm import Session

from models.category import Category
from models.position import Position


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        category = Category(name=name, parent_id=parent_id)
        self.session.add(category)
        self.session.commit()
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        return Category.get_by_id(self.session, category_id)

    def get_all_categories(self) -> List[Category]:
        return Category.get_all(self.session)

    def move_category(self, category_id: int, new_parent_id: Optional[int]) -> Category:
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
                # Простая проверка на цикл
                current = parent
                while current:
                    if current.id == category_id:
                        raise ValueError("Операция создаст цикл в иерархии")
                    current = current.parent

        category.parent_id = new_parent_id
        self.session.commit()
        return category
    
    def delete_category(self, category_id: int, cascade: bool = False) -> None:
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
    
    def update_category(self, category_id, **kwargs):
        if not kwargs:
            return False, "Нет полей для обновления", None
        
        category = self.get_category(category_id)
        if not category:
            return False, "Категория не найдена", None
        
        # Обновляем только переданные поля
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
            else:
                return False, f"Поле '{key}' не существует", None
        
        try:
            self.session.commit()
            updated_fields = ', '.join(kwargs.keys())
            return True, f"Категория обновлена: {updated_fields}", category
        except Exception as e:
            self.session.rollback()
            return False, f"Ошибка при обновлении: {str(e)}", None

    def delete_all(self) -> int:
        try:
            deleted_count = self.session.query(Category).delete()
            self.session.commit()
            return deleted_count
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ошибка при удалении категорий: {str(e)}")
        
    def get_descendants_with_level(self, session, category_id: int, level: int = 1):
        result = []

        children = (
            session.query(Category)
            .filter(Category.parent_id == category_id)
            .order_by(Category.id)
            .all()
        )

        for child in children:
            result.append((child, level))
            result.extend(self.get_descendants_with_level(session, child.id, level + 1))

        return result
    
    def get_all_parents(self, category: Category):
        parents = []
        current = category.parent

        while current:
            parents.append(current)
            current = current.parent

        return parents

    def get_tree(self, start_category_id: int | None = None, level: int = 0):
        result = []

        if start_category_id is not None and level == 0:
            start_category = self.session.query(Category).filter(Category.id == start_category_id).first()
            if not start_category:
                return []
            categories = [start_category]
        else:
            categories = (
                self.session.query(Category)
                .filter(Category.parent_id == start_category_id)
                .order_by(Category.id)
                .all()
            )

        for cat in categories:
            result.append(("category", cat, level))

            positions = (
                self.session.query(Position)
                .filter(Position.category_id == cat.id)
                .order_by(Position.id)
                .all()
            )
            for pos in positions:
                result.append(("position", pos, level + 1))

            result.extend(self.get_tree(cat.id, level + 1))

        return result
    