import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from models import Unit, EnumType, EnumValue, Category, Position, Parameter
from repository.category_parameter_repository import CategoryParameterRepository
from repository.position_parameter_repository import PositionParameterRepository

TEST_DATA_PATH = Path(__file__).parent.parent.parent / "data/test_data.json"

PARAM_TYPES = {
    "real":     ("Вещественное", 1),
    "integer":  ("Целое",        2),
    "string":   ("Строковое",    3),
    "datetime": ("Дата/время",   4),
    "enum":     ("Перечисление", 5),
}

# (short_name, display_name, type_code, unit_code_or_None)
NUMERIC_PARAMETERS = [
    ("weight",    "Вес",          "real",    "g"),
    ("calories",  "Калорийность", "real",    None),
    ("protein",   "Белки",        "real",    None),
    ("fat",       "Жиры",         "real",    None),
    ("carbs",     "Углеводы",     "real",    None),
    ("is_liquid", "Жидкость",     "integer", None),
    ("is_hot",    "Горячее",      "integer", None),
]

# (short_name, display_name, enum_type_code)
ENUM_PARAMETERS = [
    ("diet_type",      "Диета",                "diet"),
    ("allergen",       "Аллерген",             "allergen"),
    ("cooking_method", "Способ приготовления", "cooking_method"),
    ("meal_type",      "Тип приёма пищи",      "meal_type"),
]

# Maps each enum_type_code to the parameter short_name
ENUM_TYPE_TO_PARAM = {et: sn for sn, _, et in ENUM_PARAMETERS}


def _get_or_create_param_type(session: Session) -> tuple[EnumType, dict]:
    param_type = session.query(EnumType).filter_by(code="param_type").first()
    if not param_type:
        param_type = EnumType(name="Тип параметра", code="param_type")
        session.add(param_type)
        session.flush()

    type_map = {}
    for code, (name, order) in PARAM_TYPES.items():
        ev = session.query(EnumValue).filter_by(enum_type_id=param_type.id, code=code).first()
        if not ev:
            ev = EnumValue(enum_type_id=param_type.id, order_number=order, name=name, code=code)
            session.add(ev)
            session.flush()
        type_map[code] = ev.id

    return param_type, type_map


def _seed_units(session: Session, data: dict) -> dict:
    unit_map = {}
    for u in data.get("units", []):
        unit = session.query(Unit).filter_by(code=u["code"]).first()
        if not unit:
            unit = Unit(**u)
            session.add(unit)
            session.flush()
        unit_map[u["code"]] = unit.id
    return unit_map


def _seed_enums(session: Session, data: dict) -> tuple[dict, dict]:
    enum_type_map = {}
    for t in data.get("enum_types", []):
        et = session.query(EnumType).filter_by(code=t["code"]).first()
        if not et:
            et = EnumType(**t)
            session.add(et)
            session.flush()
        enum_type_map[t["code"]] = et.id

    enum_value_map = {}
    for v in data.get("enum_values", []):
        et_id = enum_type_map.get(v["type"])
        if not et_id:
            continue
        ev = session.query(EnumValue).filter_by(enum_type_id=et_id, code=v.get("code")).first()
        if not ev:
            ev = EnumValue(
                enum_type_id=et_id,
                order_number=v["order"],
                name=v["name"],
                code=v.get("code"),
            )
            session.add(ev)
            session.flush()
        enum_value_map[v["code"]] = ev.id

    return enum_type_map, enum_value_map


def _seed_categories(session: Session, data: dict) -> dict:
    category_map = {}
    for c in data.get("categories", []):
        parent_id = category_map.get(c.get("parent"))
        cat = session.query(Category).filter_by(name=c["name"]).first()
        if not cat:
            cat = Category(name=c["name"], parent_id=parent_id)
            session.add(cat)
            session.flush()
        category_map[c["name"]] = cat.id
    return category_map


def _seed_parameters(
    session: Session,
    type_map: dict,
    unit_map: dict,
    enum_type_map: dict,
) -> dict:
    param_map = {}

    for short_name, name, type_code, unit_code in NUMERIC_PARAMETERS:
        param = session.query(Parameter).filter_by(short_name=short_name).first()
        if not param:
            param = Parameter(
                short_name=short_name,
                name=name,
                param_type_id=type_map[type_code],
                unit_id=unit_map.get(unit_code) if unit_code else None,
            )
            session.add(param)
            session.flush()
        param_map[short_name] = param

    enum_type_id = type_map["enum"]
    for short_name, name, enum_type_code in ENUM_PARAMETERS:
        param = session.query(Parameter).filter_by(short_name=short_name).first()
        if not param:
            param = Parameter(
                short_name=short_name,
                name=name,
                param_type_id=enum_type_id,
                enum_type_id=enum_type_map.get(enum_type_code),
            )
            session.add(param)
            session.flush()
        param_map[short_name] = param

    return param_map


def seed_db(session: Session) -> None:
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    _, type_map = _get_or_create_param_type(session)
    unit_map = _seed_units(session, data)
    enum_type_map, enum_value_map = _seed_enums(session, data)
    category_map = _seed_categories(session, data)
    param_map = _seed_parameters(session, type_map, unit_map, enum_type_map)

    # Build enum_value_code → enum_type_code lookup for position enum values
    code_to_enum_type = {v["code"]: v["type"] for v in data.get("enum_values", [])}

    cat_param_repo = CategoryParameterRepository(session)
    pos_param_repo = PositionParameterRepository(session)

    root_category = session.query(Category).filter(Category.parent_id.is_(None)).first()
    if root_category:
        all_params = list(NUMERIC_PARAMETERS) + [(sn, n, "enum", None) for sn, n, _ in ENUM_PARAMETERS]
        for i, (short_name, *_) in enumerate(all_params):
            cat_param_repo.add_to_category(
                category_id=root_category.id,
                parameter_id=param_map[short_name].id,
                order_num=i + 1,
            )

    for p in data.get("positions", []):
        _existing = session.query(Position).filter_by(name=p["name"]).first()
        if not _existing:
            _existing = Position(
                category_id=category_map[p["category"]],
                name=p["name"],
            )
            session.add(_existing)
            session.flush()
        position: Position = _existing

        def write_num(short_name: str, val_real=None, val_int=None):
            p_obj = param_map.get(short_name)
            if p_obj is not None:
                pos_param_repo.upsert(position.id, p_obj.id, val_real=val_real, val_int=val_int)

        if p.get("weight") is not None:
            write_num("weight", val_real=float(p["weight"]))
        if p.get("calories") is not None:
            write_num("calories", val_real=float(p["calories"]))
        if p.get("protein") is not None:
            write_num("protein", val_real=float(p["protein"]))
        if p.get("fat") is not None:
            write_num("fat", val_real=float(p["fat"]))
        if p.get("carbs") is not None:
            write_num("carbs", val_real=float(p["carbs"]))
        if p.get("is_liquid") is not None:
            write_num("is_liquid", val_int=int(p["is_liquid"]))
        if p.get("is_hot") is not None:
            write_num("is_hot", val_int=int(p["is_hot"]))

        # Write the first enum value per enum_type found in the position's enum_values list
        written_enum_types: set = set()
        for ev_code in p.get("enum_values", []):
            ev_type = code_to_enum_type.get(ev_code)
            if ev_type is None:
                continue
            param_name = ENUM_TYPE_TO_PARAM.get(ev_type)
            if param_name and ev_type not in written_enum_types:
                param = param_map.get(param_name)
                ev_id = enum_value_map.get(ev_code)
                if param and ev_id:
                    pos_param_repo.upsert(position.id, param.id, enum_val_id=ev_id)
                    written_enum_types.add(ev_type)

    session.commit()


def clear_db(session: Session) -> None:
    session.execute(text("DELETE FROM position_parameters"))
    session.execute(text("DELETE FROM category_parameters"))
    session.execute(text("DELETE FROM parameters"))
    session.query(Position).delete()
    session.query(Category).delete()
    session.query(EnumValue).delete()
    session.query(EnumType).delete()
    session.query(Unit).delete()
    session.commit()
