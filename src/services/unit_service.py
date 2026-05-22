from typing import List
from sqlalchemy.orm import Session

from repository.unit_repository import UnitRepository
from models.unit import Unit


class UnitService:
    def __init__(self, session: Session):
        self.repo = UnitRepository(session)

    def get_all(self) -> List[Unit]:
        return self.repo.get_all()

    def get_by_id(self, unit_id: int) -> Unit:
        unit = self.repo.get_by_id(unit_id)
        if not unit:
            raise ValueError("Единица измерения не найдена")
        return unit

    def create(self, data: dict) -> Unit:
        return self.repo.create(data)

    def update(self, unit_id: int, data: dict) -> Unit:
        return self.repo.update(unit_id, data)

    def delete(self, unit_id: int) -> None:
        self.repo.delete(unit_id)
