from typing import List, Optional
from sqlalchemy.orm import Session

from repository.parameter_repository import ParameterRepository
from models.parameter import Parameter


class ParameterService:
    def __init__(self, session: Session):
        self.repo = ParameterRepository(session)

    def get_all(self) -> List[Parameter]:
        return self.repo.get_all()

    def get_by_id(self, param_id: int) -> Parameter:
        param = self.repo.get_by_id(param_id)
        if not param:
            raise ValueError(f"Параметр {param_id} не найден")
        return param

    def create(
        self,
        short_name: str,
        name: str,
        param_type_code: str,
        enum_type_id: Optional[int] = None,
        unit_id: Optional[int] = None,
    ) -> Parameter:
        return self.repo.add_parameter(
            short_name=short_name,
            name=name,
            param_type_code=param_type_code,
            enum_type_id=enum_type_id,
            unit_id=unit_id,
        )

    def delete(self, param_id: int) -> None:
        self.get_by_id(param_id)
        self.repo.delete_parameter(param_id)
