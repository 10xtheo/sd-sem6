from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from models.position_parameter import PositionParameter
from models.parameter import Parameter
from models.position import Position
from models.category_parameter import CategoryParameter

class PositionParameterRepository:
    def __init__(self, session: Session):
        self.session = session

    def write_value(
        self,
        position_id: int,
        parameter_id: int,
        val_real: Optional[float] = None,
        val_int: Optional[int] = None,
        val_str: Optional[str] = None,
        val_dt: Optional[str] = None,
        enum_val_id: Optional[int] = None,
    ):
        """Универсальная запись значения параметра"""
        pp = PositionParameter(
            position_id=position_id,
            parameter_id=parameter_id,
            val_real=val_real,
            val_int=val_int,
            val_str=val_str,
            val_dt=val_dt,
            enum_val_id=enum_val_id,
        )
        self.session.merge(pp)
        self.session.commit()

    def get_for_position(self, position_id: int):
        position = self.session.get(Position, position_id)
        if not position:
            raise Exception(f"Position {position_id} not found")

        stmt = (
            select(Parameter)
            .outerjoin(
                CategoryParameter,
                CategoryParameter.parameter_id == Parameter.id
            )
            .outerjoin(
                PositionParameter,
                PositionParameter.parameter_id == Parameter.id
            )
            .where(
                or_(
                    CategoryParameter.category_id == position.category_id,
                    PositionParameter.position_id == position_id
                )
            )
            .distinct()
            .order_by(Parameter.short_name)
        )

        return self.session.scalars(stmt).all()
