from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.category import Category
from models.category_parameter import CategoryParameter


class CategoryParameterRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_to_category(
        self,
        category_id: int,
        parameter_id: int,
        order_num: int = 0,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> None:
        """Upserts a parameter for a category and all its descendants."""
        self.session.merge(CategoryParameter(
            category_id=category_id,
            parameter_id=parameter_id,
            order_num=order_num,
            min_val=min_val,
            max_val=max_val,
        ))

        descendant_ids = self._get_descendant_ids(category_id)
        if descendant_ids:
            existing = {
                cp.category_id
                for cp in self.session.query(CategoryParameter.category_id)
                .filter(
                    CategoryParameter.category_id.in_(descendant_ids),
                    CategoryParameter.parameter_id == parameter_id,
                )
                .all()
            }
            to_add = [
                CategoryParameter(
                    category_id=did,
                    parameter_id=parameter_id,
                    order_num=order_num,
                    min_val=min_val,
                    max_val=max_val,
                )
                for did in descendant_ids
                if did not in existing
            ]
            if to_add:
                self.session.bulk_save_objects(to_add)

        self.session.commit()

    def inherit_from_parent(self, child_category_id: int, parent_category_id: int) -> None:
        """Copies all parameters from a parent category to a new child category."""
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == parent_category_id)
            .order_by(CategoryParameter.order_num)
        )
        for cp in self.session.scalars(stmt).all():
            self.session.add(CategoryParameter(
                category_id=child_category_id,
                parameter_id=cp.parameter_id,
                order_num=cp.order_num,
                min_val=cp.min_val,
                max_val=cp.max_val,
            ))

    def get_for_category(self, category_id: int) -> List[CategoryParameter]:
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == category_id)
            .order_by(CategoryParameter.order_num)
        )
        return list(self.session.scalars(stmt).all())

    def exists(self, category_id: int, parameter_id: int) -> bool:
        return (
            self.session.query(CategoryParameter)
            .filter(
                CategoryParameter.category_id == category_id,
                CategoryParameter.parameter_id == parameter_id,
            )
            .first()
        ) is not None

    def delete_from_category(self, category_id: int, parameter_id: int) -> int:
        all_ids = [category_id] + self._get_descendant_ids(category_id)
        deleted = (
            self.session.query(CategoryParameter)
            .filter(
                CategoryParameter.category_id.in_(all_ids),
                CategoryParameter.parameter_id == parameter_id,
            )
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return deleted

    def _get_descendant_ids(self, category_id: int) -> List[int]:
        ids = []
        children = (
            self.session.query(Category)
            .filter(Category.parent_id == category_id)
            .all()
        )
        for child in children:
            ids.append(child.id)
            ids.extend(self._get_descendant_ids(child.id))
        return ids
