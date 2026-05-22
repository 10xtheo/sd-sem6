from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_session
from services.category_parameter_service import CategoryParameterService
from schemas.category_parameter import CategoryParameterCreate, CategoryParameterOut
from schemas.common import MessageOut

router = APIRouter(prefix="/category-parameters", tags=["category-parameters"])


def get_service(session: Session = Depends(get_session)) -> CategoryParameterService:
    return CategoryParameterService(session)


@router.post("/", response_model=MessageOut, status_code=201)
def add_parameter_to_category(
    data: CategoryParameterCreate,
    service: CategoryParameterService = Depends(get_service),
):
    try:
        service.add(
            category_id=data.category_id,
            parameter_id=data.parameter_id,
            order_num=data.order_num,
            min_val=data.min_val,
            max_val=data.max_val,
        )
        return MessageOut(detail="Параметр добавлен к категории и всем дочерним")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category/{category_id}", response_model=List[CategoryParameterOut])
def get_category_parameters(
    category_id: int,
    service: CategoryParameterService = Depends(get_service),
):
    return service.get_for_category(category_id)


@router.delete("/{category_id}/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter_from_category(
    category_id: int,
    parameter_id: int,
    service: CategoryParameterService = Depends(get_service),
):
    try:
        service.delete(category_id, parameter_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
