import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from models import Unit, EnumType, EnumValue, Category, Position
from models.position_enum_values import position_enum_values

router = APIRouter(prefix="/settings", tags=["settings"])

TEST_DATA_PATH = Path(__file__).parent.parent.parent / "data/test_data.json"

def seed_db(session: Session):
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    unit_map = {}
    type_map = {}
    value_map = {}
    category_map = {}

    # UNITS
    for u in data["units"]:
        obj = session.query(Unit).filter_by(code=u["code"]).first()
        if not obj:
            obj = Unit(**u)
            session.add(obj)
            session.flush()
        unit_map[u["code"]] = obj.id

    # ENUM TYPES
    for t in data["enum_types"]:
        obj = session.query(EnumType).filter_by(code=t["code"]).first()
        if not obj:
            obj = EnumType(**t)
            session.add(obj)
            session.flush()
        type_map[t["code"]] = obj.id

    # ENUM VALUES
    for v in data["enum_values"]:
        obj = (
            session.query(EnumValue)
            .filter_by(
                enum_type_id=type_map[v["type"]],
                order_number=v["order"]
            )
            .first()
        )
        if not obj:
            obj = EnumValue(
                enum_type_id=type_map[v["type"]],
                order_number=v["order"],
                name=v["name"],
                code=v["code"],
            )
            session.add(obj)
            session.flush()

        value_map[v["code"]] = obj.id

    # CATEGORIES 
    for c in data["categories"]:
        parent_id = category_map.get(c.get("parent"))

        obj = session.query(Category).filter_by(name=c["name"]).first()
        if not obj:
            obj = Category(name=c["name"], parent_id=parent_id)
            session.add(obj)
            session.flush()

        category_map[c["name"]] = obj.id

    # POSITIONS 
    for p in data["positions"]:
        obj = session.query(Position).filter_by(name=p["name"]).first()

        if not obj:
            obj = Position(
                category_id=category_map[p["category"]],
                name=p["name"],
                weight=p.get("weight"),
                calories=p.get("calories"),
                protein=p.get("protein"),
                fat=p.get("fat"),
                carbs=p.get("carbs"),
                is_liquid=p.get("is_liquid", False),
                is_hot=p.get("is_hot", False),
                weight_unit_id=unit_map.get(p.get("unit")),
            )
            session.add(obj)
            session.flush()

            for ev_code in p.get("enum_values", []):
                session.execute(
                position_enum_values.insert().values(
                    position_id=obj.id,
                    enum_value_id=value_map[ev_code]
                )
)

    session.commit()

@router.post("/seed")
def seed(session: Session = Depends(get_session)):
    try:
        seed_db(session)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}

@router.post("/clear")
def clear(session: Session = Depends(get_session)):
    session.execute(position_enum_values.delete())
    session.query(Position).delete()
    session.query(EnumValue).delete()
    session.query(EnumType).delete()
    session.query(Category).delete()
    session.query(Unit).delete()
    session.commit()

    return {"status": "cleared"}
