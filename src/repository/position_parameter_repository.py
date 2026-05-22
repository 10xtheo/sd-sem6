from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.position_parameter import PositionParameter
from models.parameter import Parameter
from models.category_parameter import CategoryParameter
from models.position import Position


class PositionParameterRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_param_with_bounds(
        self,
        parameter_id: int,
        category_id: int,
    ) -> Optional[Tuple[Parameter, Optional[float], Optional[float]]]:
        """Returns (Parameter, min_val, max_val) for the given category, or None."""
        stmt = (
            select(Parameter, CategoryParameter.min_val, CategoryParameter.max_val)
            .join(CategoryParameter, CategoryParameter.parameter_id == Parameter.id)
            .where(CategoryParameter.category_id == category_id, Parameter.id == parameter_id)
        )
        row = self.session.execute(stmt).first()
        if not row:
            return None
        return row[0], row[1], row[2]

    def upsert(
        self,
        position_id: int,
        parameter_id: int,
        val_real: Optional[float] = None,
        val_int: Optional[int] = None,
        val_str: Optional[str] = None,
        val_dt: Optional[str] = None,
        enum_val_id: Optional[int] = None,
    ) -> None:
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

    def copy_from_category(self, position_id: int, category_id: int) -> None:
        """Creates empty PositionParameter rows for all parameters of the given category."""
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == category_id)
            .order_by(CategoryParameter.order_num)
        )
        for cp in self.session.scalars(stmt).all():
            self.session.add(PositionParameter(
                position_id=position_id,
                parameter_id=cp.parameter_id,
            ))

    def copy_missing_from_category(self, position_id: int, category_id: int) -> None:
        """Adds empty PositionParameter rows for category params the position doesn't have yet."""
        existing_ids = {
            pp.parameter_id
            for pp in self.session.query(PositionParameter)
            .filter(PositionParameter.position_id == position_id)
            .all()
        }
        stmt = (
            select(CategoryParameter)
            .where(CategoryParameter.category_id == category_id)
            .order_by(CategoryParameter.order_num)
        )
        for cp in self.session.scalars(stmt).all():
            if cp.parameter_id not in existing_ids:
                self.session.add(PositionParameter(
                    position_id=position_id,
                    parameter_id=cp.parameter_id,
                ))
        self.session.commit()

    def get_for_position(self, position_id: int):
        stmt = (
            select(Parameter)
            .outerjoin(CategoryParameter, CategoryParameter.parameter_id == Parameter.id)
            .outerjoin(PositionParameter, PositionParameter.parameter_id == Parameter.id)
            .where(
                PositionParameter.position_id == position_id,
            )
            .distinct()
            .order_by(Parameter.short_name)
        )
        return self.session.scalars(stmt).all()

    def delete(self, position_id: int, parameter_id: int) -> bool:
        deleted = self.session.query(PositionParameter).filter(
            PositionParameter.position_id == position_id,
            PositionParameter.parameter_id == parameter_id,
        ).delete(synchronize_session=False)
        self.session.commit()
        return deleted > 0
