from typing import Optional, List
from sqlalchemy.orm import Session

from repository.category_parameter_repository import CategoryParameterRepository
from models.category_parameter import CategoryParameter


class CategoryParameterService:
    def __init__(self, session: Session):
        self.repo = CategoryParameterRepository(session)

    def add(
        self,
        category_id: int,
        parameter_id: int,
        order_num: int = 0,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> None:
        self.repo.add_to_category(
            category_id=category_id,
            parameter_id=parameter_id,
            order_num=order_num,
            min_val=min_val,
            max_val=max_val,
        )

    def get_for_category(self, category_id: int) -> List[CategoryParameter]:
        return self.repo.get_for_category(category_id)

    def delete(self, category_id: int, parameter_id: int) -> None:
        if not self.repo.exists(category_id, parameter_id):
            raise ValueError(
                f"Параметр {parameter_id} не найден у категории {category_id}"
            )
        self.repo.delete_from_category(category_id, parameter_id)
