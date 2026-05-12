import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_session
from models import Unit, EnumType, EnumValue, Category, Position, Parameter
from repository.parameter_repository import ParameterRepository
from repository.category_parameter_repository import CategoryParameterRepository
from repository.position_parameter_repository import PositionParameterRepository

router = APIRouter(prefix="/settings", tags=["settings"])

TEST_DATA_PATH = Path(__file__).parent.parent.parent / "data/test_data.json"


def seed_db(session: Session):
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ==================== 0. ИНИЦИАЛИЗАЦИЯ PARAM_TYPE (КРИТИЧНО) ====================
    param_type = session.query(EnumType).filter_by(code='param_type').first()
    if not param_type:
        param_type = EnumType(name='Тип параметра', code='param_type')
        session.add(param_type)
        session.flush()

    # Создаём типы параметров, если их нет
    param_types = {
        'real': ('Вещественное', 1),
        'integer': ('Целое', 2),
        'string': ('Строковое', 3),
        'datetime': ('Дата/время', 4),
        'enum': ('Перечисление', 5),
    }

    param_type_map = {}  # code -> id
    for code, (name, order) in param_types.items():
        ev = session.query(EnumValue).filter_by(enum_type_id=param_type.id, code=code).first()
        if not ev:
            ev = EnumValue(
                enum_type_id=param_type.id,
                order_number=order,
                name=name,
                code=code
            )
            session.add(ev)
            session.flush()
        param_type_map[code] = ev.id

    print("✅ Типы параметров инициализированы")

    # ==================== 1. UNITS ====================
    unit_map = {}
    for u in data.get("units", []):
        unit = session.query(Unit).filter_by(code=u["code"]).first()
        if not unit:
            unit = Unit(**u)
            session.add(unit)
            session.flush()
        unit_map[u["code"]] = unit.id

    # ==================== 2. ENUM TYPES & VALUES (прикладные) ====================
    enum_type_map = {}
    enum_value_map = {}

    for t in data.get("enum_types", []):
        et = session.query(EnumType).filter_by(code=t["code"]).first()
        if not et:
            et = EnumType(**t)
            session.add(et)
            session.flush()
        enum_type_map[t["code"]] = et.id

    for v in data.get("enum_values", []):
        et_id = enum_type_map.get(v["type"])
        if not et_id:
            continue
        ev = session.query(EnumValue).filter_by(
            enum_type_id=et_id, order_number=v["order"]
        ).first()
        if not ev:
            ev = EnumValue(
                enum_type_id=et_id,
                order_number=v["order"],
                name=v["name"],
                code=v.get("code")
            )
            session.add(ev)
            session.flush()
        enum_value_map[v["code"]] = ev.id

    # ==================== 3. CATEGORIES ====================
    category_map = {}
    for c in data.get("categories", []):
        parent_id = category_map.get(c.get("parent"))
        cat = session.query(Category).filter_by(name=c["name"]).first()
        if not cat:
            cat = Category(name=c["name"], parent_id=parent_id)
            session.add(cat)
            session.flush()
        category_map[c["name"]] = cat.id

    # ==================== 4. PARAMETERS ====================
    param_repo = ParameterRepository(session)
    cat_param_repo = CategoryParameterRepository(session)

    # Основные параметры
    parameters = {
        "weight": param_repo.create("weight", "Вес", "real", unit_id=unit_map.get("g")),
        "calories": param_repo.create("calories", "Калорийность", "integer"),
        "protein": param_repo.create("protein", "Белки", "integer"),
        "fat": param_repo.create("fat", "Жиры", "integer"),
        "carbs": param_repo.create("carbs", "Углеводы", "integer"),
        "is_liquid": param_repo.create("is_liquid", "Является жидкостью", "integer"),
        "is_hot": param_repo.create("is_hot", "Горячее блюдо", "integer"),
    }

    # Привязываем параметры ко всем категориям (через корневую)
    root_category = session.query(Category).filter(Category.parent_id.is_(None)).first()
    if root_category:
        for param in parameters.values():
            cat_param_repo.add_to_category(
                category_id=root_category.id,
                parameter_id=param.id,
                order_num=10
            )

    # ==================== 5. POSITIONS + PARAMETER VALUES ====================
    pos_param_repo = PositionParameterRepository(session)

    for p in data.get("positions", []):
        position = session.query(Position).filter_by(name=p["name"]).first()
        if not position:
            position = Position(
                category_id=category_map[p["category"]],
                name=p["name"],
            )
            session.add(position)
            session.flush()

        # Заполняем параметры
        if p.get("weight"):
            pos_param_repo.write_value(position.id, parameters["weight"].id, val_real=float(p["weight"]))
        if p.get("calories"):
            pos_param_repo.write_value(position.id, parameters["calories"].id, val_int=p["calories"])
        if p.get("protein"):
            pos_param_repo.write_value(position.id, parameters["protein"].id, val_int=p["protein"])
        if p.get("fat"):
            pos_param_repo.write_value(position.id, parameters["fat"].id, val_int=p["fat"])
        if p.get("carbs"):
            pos_param_repo.write_value(position.id, parameters["carbs"].id, val_int=p["carbs"])

        if p.get("is_liquid") is not None:
            pos_param_repo.write_value(position.id, parameters["is_liquid"].id, val_int=int(p["is_liquid"]))
        if p.get("is_hot") is not None:
            pos_param_repo.write_value(position.id, parameters["is_hot"].id, val_int=int(p["is_hot"]))

    session.commit()
    print("✅ Seed completed successfully with new parameter system!")


@router.post("/seed")
def seed(session: Session = Depends(get_session)):
    try:
        seed_db(session)
        return {"status": "ok", "message": "Данные успешно загружены"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
def clear(session: Session = Depends(get_session)):
    session.execute(text("DELETE FROM position_parameters"))
    session.execute(text("DELETE FROM category_parameters"))
    session.execute(text("DELETE FROM parameters"))
    session.query(Position).delete()
    session.query(Category).delete()
    session.query(EnumValue).delete()
    session.query(EnumType).delete()
    session.query(Unit).delete()
    session.commit()
    return {"status": "cleared"}
