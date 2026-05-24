from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_session
from models import Category, Position
from repository.category_repository import CategoryRepository
from repository.position_repository import PositionRepository
from schemas.stats import StatsSummary, StatsByCategory, IntegrityReport, IntegrityIssue

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def get_summary(session: Session = Depends(get_session)):
    return StatsSummary(
        categories_total=session.query(Category).count(),
        categories_root=session.query(Category).filter(Category.parent_id.is_(None)).count(),
        positions_total=session.query(Position).count(),
    )


@router.get("/by-category", response_model=List[StatsByCategory])
def stats_by_category(session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    pos_repo = PositionRepository(session)
    return [
        StatsByCategory(
            id=cat.id,
            name=cat.name,
            children_count=len(cat_repo.get_children(cat.id)),
            positions_count=len(pos_repo.get_by_category(cat.id)),
        )
        for cat in cat_repo.get_all()
    ]


@router.get("/integrity", response_model=IntegrityReport)
def check_integrity(session: Session = Depends(get_session)):
    cat_repo = CategoryRepository(session)
    issues: List[IntegrityIssue] = []

    for cat in cat_repo.get_all():
        if cat.parent_id == cat.id:
            issues.append(IntegrityIssue(type="self_reference", category_id=cat.id))
        if cat.parent_id and not cat_repo.get(cat.parent_id):
            issues.append(IntegrityIssue(
                type="missing_parent",
                category_id=cat.id,
                parent_id=cat.parent_id,
            ))

    pos_repo = PositionRepository(session)
    for pos in pos_repo.get_all():
        if not cat_repo.get(pos.category_id):
            issues.append(IntegrityIssue(
                type="missing_category",
                position_id=pos.id,
                category_id=pos.category_id,
            ))

    return IntegrityReport(ok=len(issues) == 0, issues=issues)
