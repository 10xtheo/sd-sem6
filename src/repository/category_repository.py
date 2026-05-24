from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str, parent_id: Optional[int] = None) -> Category:
        category = Category(name=name, parent_id=parent_id)
        self.session.add(category)
        self.session.flush()
        return category

    def get(self, category_id: int) -> Optional[Category]:
        return self.session.get(Category, category_id)

    def get_all(self) -> List[Category]:
        return list(self.session.execute(select(Category)).scalars().all())

    def get_children(self, parent_id: Optional[int]) -> List[Category]:
        return list(self.session.execute(
            select(Category)
            .where(Category.parent_id == parent_id)
            .order_by(Category.id)
        ).scalars().all())

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

    def get_parents(self, category: Category) -> List[Category]:
        parents = []
        current = category.parent
        while current:
            parents.append(current)
            current = current.parent
        return parents

    def delete(self, category_id: int) -> None:
        category = self.get(category_id)
        if category:
            self.session.delete(category)
            self.session.commit()

    def delete_all(self) -> int:
        deleted = self.session.query(Category).delete()
        self.session.commit()
        return deleted
