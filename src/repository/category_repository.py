from typing import List, Optional
from sqlalchemy import select
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
        return self.session.get(Category, category_id)

    def get_all_categories(self) -> List[Category]:
        return list(self.session.execute(select(Category)).scalars().all())

    def move_category(self, category_id: int, new_parent_id: Optional[int]) -> Category:
        category = self.get_category(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена")

        if new_parent_id:
            if category_id == new_parent_id:
                raise ValueError("Категория не может быть родителем самой себя")

            parent = self.get_category(new_parent_id)
            if parent:
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

        children = list(self.session.execute(
            select(Category).where(Category.parent_id == category.id).order_by(Category.id)
        ).scalars().all())
        if children and not cascade:
            children_ids = [c.id for c in children]
            raise ValueError(
                f"Категория имеет потомков: {children_ids}. "
                "Используйте cascade=True для каскадного удаления"
            )

        self.session.delete(category)
        self.session.commit()

    def update_category(self, category_id: int, **kwargs):
        if not kwargs:
            return False, "Нет полей для обновления", None

        category = self.get_category(category_id)
        if not category:
            return False, "Категория не найдена", None

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

    def get_children(self, category_id: int) -> List[Category]:
        return (
            list(self.session.execute(
                select(Category).where(Category.parent_id == category_id).order_by(Category.id)
            ).scalars().all())
        )

    def get_descendants_with_level(self, category_id: int, level: int = 1):
        result = []
        children = (
            self.session.query(Category)
            .filter(Category.parent_id == category_id)
            .order_by(Category.id)
            .all()
        )
        for child in children:
            result.append((child, level))
            result.extend(self.get_descendants_with_level(child.id, level + 1))
        return result

    def get_all_parents(self, category: Category) -> List[Category]:
        parents = []
        current = category.parent
        while current:
            parents.append(current)
            current = current.parent
        return parents

    def get_tree(self, start_category_id: Optional[int] = None, level: int = 0):
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
