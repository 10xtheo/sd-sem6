from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database import get_session
from services.category_service import CategoryService
from schemas.category import CategoryCreate, CategoryUpdate, CategoryMove, CategoryOut
from schemas.tree import TreeResponse
from utils.filters import parse_param_filters

router = APIRouter(prefix="/categories", tags=["categories"])


def get_service(session: Session = Depends(get_session)) -> CategoryService:
    return CategoryService(session)


@router.get("/tree", response_model=TreeResponse)
def get_tree(
    request: Request,
    start_id: Optional[int] = Query(None),
    service: CategoryService = Depends(get_service),
):
    param_filters = parse_param_filters(dict(request.query_params)) if request else []
    items = service.get_tree(start_id=start_id, param_filters=param_filters)
    return TreeResponse(items=items)


@router.get("/", response_model=List[CategoryOut])
def list_categories(service: CategoryService = Depends(get_service)):
    return service.get_all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, service: CategoryService = Depends(get_service)):
    try:
        return service.get_by_id(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{category_id}/children", response_model=List[CategoryOut])
def get_children(category_id: int, service: CategoryService = Depends(get_service)):
    try:
        return service.get_children(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{category_id}/descendants", response_model=List[CategoryOut])
def get_descendants(category_id: int, service: CategoryService = Depends(get_service)):
    try:
        return service.get_descendants(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{category_id}/parents", response_model=List[CategoryOut])
def get_parents(category_id: int, service: CategoryService = Depends(get_service)):
    try:
        return service.get_parents(category_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(body: CategoryCreate, service: CategoryService = Depends(get_service)):
    try:
        return service.create(name=body.name, parent_id=body.parent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{category_id}", response_model=CategoryOut)
def rename_category(category_id: int, body: CategoryUpdate, service: CategoryService = Depends(get_service)):
    try:
        return service.rename(category_id, name=body.name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{category_id}/move", response_model=CategoryOut)
def move_category(category_id: int, body: CategoryMove, service: CategoryService = Depends(get_service)):
    try:
        return service.move(category_id, new_parent_id=body.new_parent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    cascade: bool = False,
    service: CategoryService = Depends(get_service),
):
    try:
        service.delete(category_id, cascade=cascade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
