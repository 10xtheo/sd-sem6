from typing import List, Optional
from sqlalchemy.orm import Session

from models.position import Position
from repository.position_repository import PositionRepository
from repository.category_repository import CategoryRepository
from repository.position_parameter_repository import PositionParameterRepository


class PositionService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PositionRepository(session)
        self.category_repo = CategoryRepository(session)
        self.pos_param_repo = PositionParameterRepository(session)

    def get_all(self, category_id: Optional[int] = None) -> List[Position]:
        if category_id is not None:
            return self.repo.get_by_category(category_id)
        return self.repo.get_all()

    def search_by_name(self, query: str) -> List[Position]:
        return self.repo.search_by_name(query)

    def get_by_id(self, position_id: int) -> Position:
        position = self.repo.get(position_id)
        if not position:
            raise ValueError(f"Позиция {position_id} не найдена")
        return position

    def get_full(self, position_id: int) -> dict:
        result = self.repo.get_full(position_id)
        if not result:
            raise ValueError(f"Позиция {position_id} не найдена")
        return result

    def get_parents(self, position_id: int) -> list:
        position = self.get_by_id(position_id)
        return self.repo.get_category_parents(position)

    def create(self, category_id: int, name: str) -> Position:
        category = self.category_repo.get(category_id)
        if not category:
            raise ValueError(f"Категория {category_id} не найдена")

        position = self.repo.add(category_id=category_id, name=name)
        self.pos_param_repo.copy_from_category(position.id, category_id)
        self.session.commit()
        self.session.refresh(position)
        return position

    def update(self, position_id: int, name: Optional[str]) -> Position:
        position = self.get_by_id(position_id)
        if name is not None:
            position.name = name
        self.session.commit()
        self.session.refresh(position)
        return position

    def move(self, position_id: int, new_category_id: int) -> Position:
        position = self.get_by_id(position_id)
        category = self.category_repo.get(new_category_id)
        if not category:
            raise ValueError(f"Категория {new_category_id} не найдена")
        position.category_id = new_category_id
        self.session.commit()
        self.pos_param_repo.copy_missing_from_category(position_id, new_category_id)
        self.session.refresh(position)
        return position

    def delete(self, position_id: int) -> None:
        self.get_by_id(position_id)
        self.repo.delete(position_id)

    def search(
        self,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        param_filters: Optional[list] = None,
    ) -> List[Position]:
        return self.repo.get_filtered_with_params(
            name=name,
            category_id=category_id,
            param_filters=param_filters,
        )
