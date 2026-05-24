from typing import List, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, and_, or_, exists, text

from models.position import Position
from models.category import Category
from models.position_parameter import PositionParameter
from models.parameter import Parameter


class PositionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, category_id: int, name: str) -> Position:
        position = Position(category_id=category_id, name=name)
        self.session.add(position)
        self.session.flush()
        return position

    def get(self, position_id: int) -> Optional[Position]:
        return self.session.get(Position, position_id)

    def get_all(self) -> List[Position]:
        return list(self.session.execute(select(Position)).scalars().all())

    def get_by_category(self, category_id: int) -> List[Position]:
        return list(self.session.execute(
            select(Position)
            .where(Position.category_id == category_id)
            .order_by(Position.id)
        ).scalars().all())

    def search_by_name(self, query: str) -> List[Position]:
        return list(self.session.execute(
            select(Position).where(Position.name.ilike(f"%{query}%"))
        ).scalars().all())

    def get_full(self, position_id: int) -> Optional[dict]:
        position = (
            self.session.query(Position)
            .options(
                joinedload(Position.parameters).joinedload(PositionParameter.parameter).joinedload(Parameter.param_type),
                joinedload(Position.parameters).joinedload(PositionParameter.parameter).joinedload(Parameter.enum_type),
                joinedload(Position.parameters).joinedload(PositionParameter.parameter).joinedload(Parameter.unit),
                joinedload(Position.parameters).joinedload(PositionParameter.enum_value),
            )
            .filter(Position.id == position_id)
            .first()
        )
        if not position:
            return None
        return {"position": position, "position_parameters": position.parameters}

    def get_positions_with_params_for_category(
        self,
        category_id: int,
        param_filters: Optional[List[dict]] = None,
    ) -> List[Position]:
        query = (
            self.session.query(Position)
            .options(
                joinedload(Position.parameters).joinedload(PositionParameter.parameter)
            )
            .filter(Position.category_id == category_id)
        )
        if param_filters:
            query = self._apply_param_filters(query, param_filters)
        return query.order_by(Position.id).all()

    def get_filtered(
        self,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        param_filters: Optional[List[dict]] = None,
    ) -> List[Position]:
        query = self.session.query(Position)

        if name:
            query = query.filter(Position.name.ilike(f"%{name}%"))
        if category_id is not None:
            query = query.filter(Position.category_id == category_id)
        if param_filters:
            query = self._apply_param_filters(query, param_filters)

        return query.order_by(Position.id).all()

    def get_filtered_with_params(
        self,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        param_filters: Optional[List[dict]] = None,
    ) -> List[Position]:
        """Like get_filtered but also eager-loads all parameter values for serialization."""
        query = (
            self.session.query(Position)
            .options(
                selectinload(Position.parameters)
                .joinedload(PositionParameter.parameter)
                .joinedload(Parameter.param_type),
                selectinload(Position.parameters)
                .joinedload(PositionParameter.parameter)
                .joinedload(Parameter.enum_type),
                selectinload(Position.parameters)
                .joinedload(PositionParameter.parameter)
                .joinedload(Parameter.unit),
                selectinload(Position.parameters)
                .joinedload(PositionParameter.enum_value),
            )
        )

        if name:
            query = query.filter(Position.name.ilike(f"%{name}%"))
        if category_id is not None:
            query = query.filter(Position.category_id == category_id)
        if param_filters:
            query = self._apply_param_filters(query, param_filters)

        return query.order_by(Position.id).all()

    def _apply_param_filters(self, query, param_filters: List[dict]):
        from models.enum_value import EnumValue

        conditions = []

        for f in param_filters:
            short_name = f.get("short_name")
            if not short_name:
                continue

            param = self.session.query(Parameter).filter_by(short_name=short_name).first()
            if not param:
                continue

            pp_conditions = [
                PositionParameter.parameter_id == param.id,
                PositionParameter.position_id == Position.id,
            ]

            if f.get("min") is not None:
                min_v = f["min"]
                pp_conditions.append(or_(
                    PositionParameter.val_real >= min_v,
                    PositionParameter.val_int >= min_v,
                ))

            if f.get("max") is not None:
                max_v = f["max"]
                pp_conditions.append(or_(
                    PositionParameter.val_real <= max_v,
                    PositionParameter.val_int <= max_v,
                ))

            if f.get("eq") is not None:
                search = str(f["eq"]).strip()
                type_code = param.param_type.code if param.param_type else None

                if type_code == "enum" and param.enum_type_id:
                    enum_ids = self.session.query(EnumValue.id).filter(
                        EnumValue.enum_type_id == param.enum_type_id,
                        or_(
                            EnumValue.code == search,
                            EnumValue.name.ilike(f"%{search}%"),
                        ),
                    )
                    pp_conditions.append(PositionParameter.enum_val_id.in_(enum_ids))

                elif type_code == "string":
                    pp_conditions.append(PositionParameter.val_str.ilike(f"%{search}%"))

                else:
                    try:
                        num = float(search)
                        num_conds = [PositionParameter.val_real == num]
                        if num == int(num):
                            num_conds.append(PositionParameter.val_int == int(num))
                        pp_conditions.append(or_(*num_conds))
                    except ValueError:
                        pass

            if f.get("contains") is not None:
                pp_conditions.append(PositionParameter.val_str.ilike(f"%{f['contains']}%"))

            if len(pp_conditions) > 2:
                conditions.append(exists().where(and_(*pp_conditions)))

        if conditions:
            query = query.filter(and_(*conditions))

        return query

    def delete(self, position_id: int) -> None:
        position = self.get(position_id)
        if position:
            self.session.delete(position)
            self.session.commit()

    def delete_all(self) -> int:
        self.session.execute(text("DELETE FROM position_parameters"))
        deleted = self.session.query(Position).delete()
        self.session.commit()
        return deleted

    def get_category_parents(self, position: Position) -> List[Category]:
        parents = []
        current = position.category
        while current:
            parents.append(current)
            current = current.parent
        return parents
