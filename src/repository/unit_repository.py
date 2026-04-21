from sqlalchemy.orm import Session
from models.unit import Unit
from schemas.unit import UnitCreate, UnitUpdate


class UnitRepository:
    def __init__(self, session):
        self.session = session

    def create(self, data):
        unit = Unit(**data.model_dump())
        self.session.add(unit)
        self.session.commit()
        self.session.refresh(unit)
        return unit

    def get_all(self):
        return self.session.query(Unit).all()

    def get_by_id(self, unit_id: int):
        return self.session.query(Unit).filter(Unit.id == unit_id).first()

    def update(self, unit_id: int, data):
        unit = self.get_by_id(unit_id)

        if not unit:
            raise ValueError("Unit not found")

        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(unit, k, v)

        self.session.commit()
        self.session.refresh(unit)
        return unit

    def delete(self, unit_id: int):
        unit = self.get_by_id(unit_id)

        if not unit:
            raise ValueError("Unit not found")

        self.session.delete(unit)
        self.session.commit()

    def delete_all(self) -> int:
        try:
            deleted_count = self.session.query(Unit).delete()
            self.session.commit()
            return deleted_count
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ошибка при удалении единиц измерения: {str(e)}")
    