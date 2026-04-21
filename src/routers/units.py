from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from repository.unit_repository import UnitRepository
from schemas.unit import UnitCreate, UnitUpdate, UnitResponse

router = APIRouter(prefix="/units", tags=["units"])


def get_repo(session: Session = Depends(get_session)) -> UnitRepository:
    return UnitRepository(session)


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int, repo: UnitRepository = Depends(get_repo)):
    unit = repo.get_by_id(unit_id)

    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    return unit


@router.get("/")
def get_units(repo: UnitRepository = Depends(get_repo)):
    return repo.get_all()


@router.post("/", response_model=UnitResponse, status_code=201)
def create_unit(data: UnitCreate, repo: UnitRepository = Depends(get_repo)):
    try:
        return repo.create(data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    data: UnitUpdate,
    repo: UnitRepository = Depends(get_repo),
):
    try:
        return repo.update(unit_id, data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{unit_id}", status_code=204)
def delete_unit(unit_id: int, repo: UnitRepository = Depends(get_repo)):
    try:
        repo.delete(unit_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
