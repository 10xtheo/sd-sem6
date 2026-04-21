import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session, init_db
from repository import CategoryRepository, PositionRepository

router = APIRouter(prefix="/settings", tags=["settings"])

TEST_DATA_PATH = Path(__file__).parent.parent.parent / "data/test_data.json"


def _load_test_data(cat_repo: CategoryRepository, pos_repo: PositionRepository):
    with open(TEST_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    name_to_id: dict[str, int] = {}

    for cat_data in data["categories"]:
        parent_id = name_to_id.get(cat_data["parent"]) if "parent" in cat_data else None
        cat = cat_repo.add_category(name=cat_data["name"], parent_id=parent_id)
        name_to_id[cat.name] = cat.id

    for pos_data in data["positions"]:
        category_id = name_to_id.get(pos_data["category"])
        if not category_id:
            raise ValueError(f"Категория '{pos_data['category']}' не найдена")
        pos_repo.add_position(
            category_id=category_id,
            name=pos_data["name"],
            weight=pos_data.get("weight"),
            weight_unit_id=pos_data.get("weight_unit_id"),
            calories=pos_data.get("calories"),
            protein=pos_data.get("protein"),
            fat=pos_data.get("fat"),
            carbs=pos_data.get("carbs"),
            is_liquid=pos_data.get("is_liquid", False),
            is_hot=pos_data.get("is_hot", False),
        )


@router.post("/init-db")
def initialize_db():
    init_db()
    return {"detail": "База данных инициализирована"}


@router.post("/seed")
def seed_test_data(session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    pos_repo = PositionRepository(session)
    try:
        pos_repo.delete_all()
        cat_repo.delete_all()
        _load_test_data(cat_repo, pos_repo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"detail": "Тестовые данные загружены"}


@router.post("/clear")
def clear_db(session: Session = Depends(get_session)):
    pos_repo = PositionRepository(session)
    cat_repo = CategoryRepository(session)
    pos_repo.delete_all()
    cat_repo.delete_all()
    return {"detail": "База данных очищена"}
