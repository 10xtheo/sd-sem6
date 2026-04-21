from sqlalchemy.orm import Session
from models.position import Position
from models.enum_value import EnumValue


class PositionEnumRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_enum_value(self, position_id: int, enum_value_id: int):
        position = self.session.query(Position).get(position_id)
        enum_value = self.session.query(EnumValue).get(enum_value_id)

        if not position or not enum_value:
            raise ValueError("Position or EnumValue not found")

        if enum_value in position.enum_values:
            return position

        position.enum_values.append(enum_value)
        self.session.commit()
        self.session.refresh(position)
        return position

    def remove_enum_value(self, position_id: int, enum_value_id: int):
        position = self.session.query(Position).get(position_id)
        enum_value = self.session.query(EnumValue).get(enum_value_id)

        if not position or not enum_value:
            raise ValueError("Position or EnumValue not found")

        if enum_value in position.enum_values:
            position.enum_values.remove(enum_value)
            self.session.commit()

        return position

    def get_grouped(self, position_id: int):
        position = self.session.query(Position).get(position_id)

        if not position:
            raise ValueError("Position not found")

        result = {}

        for ev in position.enum_values:
            type_name = ev.enum_type.name

            if type_name not in result:
                result[type_name] = []

            result[type_name].append({
                "id": ev.id,
                "name": ev.name,
                "code": ev.code,
            })

        return result
