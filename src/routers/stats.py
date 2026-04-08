from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_session
from models import Category, Position
from repository import CategoryRepository, PositionRepository

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
def get_summary(session: Session = Depends(get_session)):
    categories_count = session.query(Category).count()
    root_categories = session.query(Category).filter(Category.parent_id.is_(None)).count()
    positions_count = session.query(Position).count()

    result = {
        "categories_total": categories_count,
        "categories_root": root_categories,
        "positions_total": positions_count,
    }

    if positions_count > 0:
        result["calories_avg"] = round(session.query(func.avg(Position.calories)).scalar() or 0, 1)
        result["calories_max"] = session.query(func.max(Position.calories)).scalar() or 0
        result["liquid_count"] = session.query(Position).filter(Position.is_liquid == True).count()
        result["hot_count"] = session.query(Position).filter(Position.is_hot == True).count()

    return result


@router.get("/by-category")
def stats_by_category(session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    pos_repo = PositionRepository(session)
    categories = cat_repo.get_all_categories()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "children_count": len(cat_repo.get_children(cat.id)),
            "positions_count": len(pos_repo.get_positions_by_category(cat.id)),
        }
        for cat in categories
    ]


@router.get("/top-calories")
def top_by_calories(limit: int = 5, session: Session = Depends(get_session)):
    positions = session.query(Position).order_by(Position.calories.desc()).limit(limit).all()
    return [
        {"id": p.id, "name": p.name, "calories": p.calories, "category": p.category.name}
        for p in positions
    ]


@router.get("/top-protein")
def top_by_protein(limit: int = 5, session: Session = Depends(get_session)):
    positions = session.query(Position).order_by(Position.protein.desc()).limit(limit).all()
    return [
        {"id": p.id, "name": p.name, "protein": p.protein, "category": p.category.name}
        for p in positions
    ]


@router.get("/integrity")
def check_integrity(session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    issues = []

    for cat in cat_repo.get_all_categories():
        if cat.parent_id == cat.id:
            issues.append({"type": "self_reference", "category_id": cat.id})
        if cat.parent_id and not cat_repo.get_category(cat.parent_id):
            issues.append({"type": "missing_parent", "category_id": cat.id, "parent_id": cat.parent_id})

    for pos in session.query(Position).all():
        if not cat_repo.get_category(pos.category_id):
            issues.append({"type": "missing_category", "position_id": pos.id, "category_id": pos.category_id})

    return {"ok": len(issues) == 0, "issues": issues}
