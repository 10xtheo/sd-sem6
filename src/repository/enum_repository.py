from sqlalchemy.orm import Session
from models.enum_type import EnumType
from models.enum_value import EnumValue


class EnumRepository:
    def __init__(self, session: Session):
        self.session = session


    # ENUM TYPE
    def create_enum_type(self, data: dict):
        obj = EnumType(**data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update_enum_type(self, type_id: int, data: dict):
        obj = self.get_enum_type(type_id)
        if not obj:
            return None

        for k, v in data.items():
            setattr(obj, k, v)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_enum_type(self, type_id: int):
        return self.session.query(EnumType).filter(EnumType.id == type_id).first()

    def get_enum_types(self):
        return self.session.query(EnumType).all()

    def delete_enum_type(self, type_id: int):
        obj = self.get_enum_type(type_id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True

    # ENUM VALUE
    def create_enum_value(self, data: dict):
        obj = EnumValue(**data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update_enum_value(self, value_id: int, data: dict):
        obj = self.get_enum_value(value_id)
        if not obj:
            return None

        for k, v in data.items():
            setattr(obj, k, v)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_enum_value(self, value_id: int):
        return self.session.query(EnumValue).filter(EnumValue.id == value_id).first()

    def get_enum_values(self):
        return self.session.query(EnumValue).all()

    def delete_enum_value(self, value_id: int):
        obj = self.get_enum_value(value_id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True

    def get_enum_values_by_type(self, type_id: int, desc: bool = False):
        query = self.session.query(EnumValue).filter(
            EnumValue.enum_type_id == type_id
        )

        order = EnumValue.order_number.desc() if desc else EnumValue.order_number.asc()
        return query.order_by(order).all()


    # VALIDATION
    def validate_value_in_type(self, type_code: str, value_name: str):
        enum_type = (
            self.session.query(EnumType)
            .filter(EnumType.code == type_code)
            .first()
        )

        if not enum_type:
            raise ValueError(f"Enum type '{type_code}' not found")

        enum_value = (
            self.session.query(EnumValue)
            .filter(
                EnumValue.enum_type_id == enum_type.id,
                EnumValue.name == value_name,
            )
            .first()
        )

        if not enum_value:
            raise ValueError(
                f"Value '{value_name}' not found in type '{type_code}'"
            )

        return enum_value