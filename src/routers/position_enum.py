from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from repository.position_enum_repository import PositionEnumRepository

router = APIRouter(prefix="/positions", tags=["position-enums"])


def get_repo(session: Session = Depends(get_session)) -> PositionEnumRepository:
    return PositionEnumRepository(session)


@router.post("/{position_id}/enum-values/{value_id}")
def add_enum_value(
    position_id: int,
    value_id: int,
    repo: PositionEnumRepository = Depends(get_repo),
):
    try:
        return repo.add_enum_value(position_id, value_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{position_id}/enum-values/{value_id}")
def remove_enum_value(
    position_id: int,
    value_id: int,
    repo: PositionEnumRepository = Depends(get_repo),
):
    try:
        return repo.remove_enum_value(position_id, value_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{position_id}/enum-values/grouped")
def get_grouped_enum_values(
    position_id: int,
    repo: PositionEnumRepository = Depends(get_repo),
):
    try:
        return repo.get_grouped(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
