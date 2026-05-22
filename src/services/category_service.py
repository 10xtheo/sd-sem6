from typing import List, Optional
from sqlalchemy.orm import Session

from models.category import Category
from repository.category_repository import CategoryRepository
from repository.position_repository import PositionRepository
from repository.category_parameter_repository import CategoryParameterRepository
from schemas.tree import TreeCategory, TreePosition, TreeParamValue, TreeItem


class CategoryService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CategoryRepository(session)
        self.position_repo = PositionRepository(session)
        self.cat_param_repo = CategoryParameterRepository(session)

    def get_all(self) -> List[Category]:
        return self.repo.get_all()

    def get_by_id(self, category_id: int) -> Category:
        category = self.repo.get(category_id)
        if not category:
            raise ValueError(f"Категория {category_id} не найдена")
        return category

    def get_children(self, category_id: int) -> List[Category]:
        self.get_by_id(category_id)
        return self.repo.get_children(category_id)

    def get_descendants(self, category_id: int) -> List[Category]:
        self.get_by_id(category_id)
        return [cat for cat, _ in self.repo.get_descendants_with_level(category_id)]

    def get_parents(self, category_id: int) -> List[Category]:
        category = self.get_by_id(category_id)
        return self.repo.get_parents(category)

    def create(self, name: str, parent_id: Optional[int] = None) -> Category:
        if parent_id is not None:
            self.get_by_id(parent_id)

        category = self.repo.add(name=name, parent_id=parent_id)

        if parent_id is not None:
            self.cat_param_repo.inherit_from_parent(category.id, parent_id)

        self.session.commit()
        self.session.refresh(category)
        return category

    def rename(self, category_id: int, name: str) -> Category:
        category = self.get_by_id(category_id)
        category.name = name
        self.session.commit()
        self.session.refresh(category)
        return category

    def move(self, category_id: int, new_parent_id: Optional[int]) -> Category:
        category = self.get_by_id(category_id)

        if new_parent_id is not None:
            if category_id == new_parent_id:
                raise ValueError("Категория не может быть родителем самой себя")
            parent = self.repo.get(new_parent_id)
            if not parent:
                raise ValueError(f"Категория {new_parent_id} не найдена")
            current = parent
            while current:
                if current.id == category_id:
                    raise ValueError("Операция создаст цикл в иерархии")
                current = current.parent

        category.parent_id = new_parent_id
        self.session.commit()

        if new_parent_id is not None:
            self._inherit_params_from_parent(category_id, new_parent_id)

        self.session.refresh(category)
        return category

    def _inherit_params_from_parent(self, category_id: int, parent_id: int) -> None:
        """Adds parameters from the new parent to the moved category and all its descendants."""
        for cp in self.cat_param_repo.get_for_category(parent_id):
            if not self.cat_param_repo.exists(category_id, cp.parameter_id):
                self.cat_param_repo.add_to_category(
                    category_id=category_id,
                    parameter_id=cp.parameter_id,
                    order_num=cp.order_num,
                    min_val=cp.min_val,
                    max_val=cp.max_val,
                )

    def delete(self, category_id: int, cascade: bool = False) -> None:
        self.get_by_id(category_id)
        children = self.repo.get_children(category_id)
        if children and not cascade:
            ids = [c.id for c in children]
            raise ValueError(
                f"Категория имеет потомков: {ids}. Используйте cascade=True для удаления"
            )
        self.repo.delete(category_id)

    def get_tree(
        self,
        start_id: Optional[int] = None,
        param_filters: Optional[list] = None,
    ) -> List[TreeItem]:
        return self._build_tree(start_id, level=0, param_filters=param_filters)

    def _build_tree(
        self,
        parent_id: Optional[int],
        level: int,
        param_filters: Optional[list],
    ) -> List[TreeItem]:
        result = []

        if parent_id is not None and level == 0:
            cat = self.repo.get(parent_id)
            if not cat:
                return []
            categories = [cat]
        else:
            categories = self.repo.get_children(parent_id)

        for cat in categories:
            result.append(TreeCategory(
                id=cat.id,
                name=cat.name,
                level=level,
                parent_id=cat.parent_id,
            ))

            positions = self.position_repo.get_positions_with_params_for_category(
                category_id=cat.id,
                param_filters=param_filters,
            )

            for pos in positions:
                params = [
                    TreeParamValue(
                        parameter_id=pp.parameter_id,
                        short_name=pp.parameter.short_name if pp.parameter else None,
                        name=pp.parameter.name if pp.parameter else None,
                        val_real=pp.val_real,
                        val_int=pp.val_int,
                        val_str=pp.val_str,
                        val_dt=str(pp.val_dt) if pp.val_dt else None,
                        enum_val_id=pp.enum_val_id,
                    )
                    for pp in pos.parameters
                ]
                result.append(TreePosition(
                    id=pos.id,
                    name=pos.name,
                    category_id=pos.category_id,
                    level=level + 1,
                    parameters=params,
                ))

            result.extend(self._build_tree(cat.id, level + 1, param_filters))

        return result
