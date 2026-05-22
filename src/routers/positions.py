from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_session
from services.position_service import PositionService
from schemas.position import PositionCreate, PositionUpdate, PositionMove, PositionOut, PositionFull
from schemas.position_parameter import PositionWithParameters
from schemas.category import CategoryOut
from utils.filters import parse_param_filters

router = APIRouter(prefix="/positions", tags=["positions"])


def get_service(session: Session = Depends(get_session)) -> PositionService:
    return PositionService(session)


@router.get("/search", response_model=List[PositionFull])
def search_positions(
    request: Request,
    name: Optional[str] = Query(None, description="Поиск по имени (частичное совпадение)"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    service: PositionService = Depends(get_service),
):
    """
    Поиск позиций по полям и значениям параметров.

    Фильтрация по параметрам через query params:
    - `{short_name}=value` — точное совпадение / поиск по значению
    - `{short_name}_min=N`  — минимальное значение числового параметра
    - `{short_name}_max=N`  — максимальное значение числового параметра
    - `{short_name}_contains=S` — строковый параметр содержит S

    Пример: `/positions/search?calories_min=100&calories_max=300&protein_min=20`
    """
    param_filters = parse_param_filters(dict(request.query_params)) if request else []
    return service.search(name=name, category_id=category_id, param_filters=param_filters)


@router.get("/", response_model=List[PositionOut])
def list_positions(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    service: PositionService = Depends(get_service),
):
    if search:
        return service.search_by_name(search)
    return service.get_all(category_id=category_id)


@router.get("/{position_id}/full", response_model=PositionWithParameters)
def get_position_full(position_id: int, service: PositionService = Depends(get_service)):
    try:
        return service.get_full(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{position_id}/parents", response_model=List[CategoryOut])
def get_position_parents(position_id: int, service: PositionService = Depends(get_service)):
    try:
        return service.get_parents(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{position_id}", response_model=PositionOut)
def get_position(position_id: int, service: PositionService = Depends(get_service)):
    try:
        return service.get_by_id(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=PositionOut, status_code=201)
def create_position(body: PositionCreate, service: PositionService = Depends(get_service)):
    try:
        return service.create(category_id=body.category_id, name=body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{position_id}", response_model=PositionOut)
def update_position(position_id: int, body: PositionUpdate, service: PositionService = Depends(get_service)):
    try:
        return service.update(position_id, name=body.name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{position_id}/move", response_model=PositionOut)
def move_position(position_id: int, body: PositionMove, service: PositionService = Depends(get_service)):
    try:
        return service.move(position_id, new_category_id=body.new_category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, service: PositionService = Depends(get_service)):
    try:
        service.delete(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
