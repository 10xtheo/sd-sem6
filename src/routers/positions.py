from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from repository import PositionRepository
from schemas import PositionCreate, PositionUpdate, PositionMove, PositionOut
from schemas.position import PositionWithCharacteristics
from schemas.enum_value import EnumValueOut
router = APIRouter(prefix="/positions", tags=["positions"])


def get_repo(session: Session = Depends(get_session)) -> PositionRepository:
    return PositionRepository(session)


@router.get("/", response_model=List[PositionOut])
def list_positions(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_calories: Optional[int] = None,
    max_calories: Optional[int] = None,
    is_liquid: Optional[bool] = None,
    is_hot: Optional[bool] = None,
    repo: PositionRepository = Depends(get_repo),
):
    if search:
        return repo.search_positions(search)
    if any(p is not None for p in [min_calories, max_calories, is_liquid, is_hot, category_id]):
        return repo.get_filtered_positions(
            min_calories=min_calories,
            max_calories=max_calories,
            is_liquid=is_liquid,
            is_hot=is_hot,
            category_id=category_id,
        )
    return repo.get_all_positions()


@router.get("/{position_id}", response_model=PositionOut)
def get_position(position_id: int, repo: PositionRepository = Depends(get_repo)):
    position = repo.get_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    return position

@router.get("/{position_id}/parents")
def get_position_parents(position_id: int, repo: PositionRepository = Depends(get_repo)):
    position = repo.get_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    parents = repo.get_position_parents(position)
    return [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in parents]

@router.post("/", response_model=PositionOut, status_code=201)
def create_position(body: PositionCreate, repo: PositionRepository = Depends(get_repo)):
    try:
        return repo.add_position(**body.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{position_id}", response_model=PositionOut)
def update_position(position_id: int, body: PositionUpdate, repo: PositionRepository = Depends(get_repo)):
    try:
        return repo.update_position(position_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{position_id}/move", response_model=PositionOut)
def move_position(position_id: int, body: PositionMove, repo: PositionRepository = Depends(get_repo)):
    try:
        return repo.move_position(position_id, body.new_category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, repo: PositionRepository = Depends(get_repo)):
    try:
        repo.delete_position(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{position_id}/full", response_model=PositionWithCharacteristics)
def get_position_full(
    position_id: int,
    desc: bool = False,
    repo: PositionRepository = Depends(get_repo),
):
    data = repo.get_position_full(position_id, desc)

    if not data:
        raise HTTPException(status_code=404, detail="Position not found")

    position = data["position"]
    grouped = data["characteristics"]

    # mapping 
    result = {
        "id": position.id,
        "name": position.name,
        "category_id": position.category_id,
        "is_liquid": position.is_liquid,
        "is_hot": position.is_hot,
        "characteristics": {
            key: [EnumValueOut.model_validate(ev) for ev in values]
            for key, values in grouped.items()
        }
    }

    return result
