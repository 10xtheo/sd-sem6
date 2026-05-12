from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from repository.position_repository import PositionRepository
from schemas.position import PositionCreate, PositionUpdate, PositionMove, PositionOut
from schemas.position_parameter import PositionWithParameters, PositionParameterValue, PositionOutMinimal


router = APIRouter(prefix="/positions", tags=["positions"])


def get_repo(session: Session = Depends(get_session)) -> PositionRepository:
    return PositionRepository(session)


@router.get("/", response_model=List[PositionOut])
def list_positions(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    repo: PositionRepository = Depends(get_repo),
):
    """Список позиций с базовой фильтрацией"""
    if search:
        return repo.search_positions(search)
    
    if category_id is not None:
        return repo.get_positions_by_category(category_id)
    
    return repo.get_all_positions()


@router.get("/{position_id}", response_model=PositionOut)
def get_position(position_id: int, repo: PositionRepository = Depends(get_repo)):
    position = repo.get_position(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    return position

# TODO: починить добавить валидацию как выше через response_model=...
@router.get("/{position_id}/full")
def get_position_full(position_id: int, repo=Depends(get_repo)):

    result = repo.get_position_full(position_id)

    if result is None:
        return None

    position, parameters = result

    return {
        "position": position,
        "parameters": parameters
    }


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
        return repo.add_position(
            category_id=body.category_id,
            name=body.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{position_id}", response_model=PositionOut)
def update_position(position_id: int, body: PositionUpdate, repo: PositionRepository = Depends(get_repo)):
    try:
        return repo.update_position(position_id, name=body.name)
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
