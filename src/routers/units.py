from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from services.unit_service import UnitService
from schemas.unit import UnitCreate, UnitUpdate, UnitResponse

router = APIRouter(prefix="/units", tags=["units"])


def get_service(session: Session = Depends(get_session)) -> UnitService:
    return UnitService(session)


@router.get("/", response_model=list[UnitResponse])
def get_units(service: UnitService = Depends(get_service)):
    return service.get_all()


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int, service: UnitService = Depends(get_service)):
    try:
        return service.get_by_id(unit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=UnitResponse, status_code=201)
def create_unit(data: UnitCreate, service: UnitService = Depends(get_service)):
    try:
        return service.create(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{unit_id}", response_model=UnitResponse)
def update_unit(unit_id: int, data: UnitUpdate, service: UnitService = Depends(get_service)):
    try:
        return service.update(unit_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{unit_id}", status_code=204)
def delete_unit(unit_id: int, service: UnitService = Depends(get_service)):
    try:
        service.delete(unit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
