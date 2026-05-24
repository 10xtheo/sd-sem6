from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_session
from services.position_parameter_service import PositionParameterService
from schemas.common import MessageOut

router = APIRouter(prefix="/position-parameters", tags=["position-parameters"])


def get_service(session: Session = Depends(get_session)) -> PositionParameterService:
    return PositionParameterService(session)


@router.post("/{position_id}/parameters/{parameter_id}", response_model=MessageOut)
def write_position_parameter(
    position_id: int,
    parameter_id: int,
    val_real: Optional[float] = None,
    val_int: Optional[int] = None,
    val_str: Optional[str] = None,
    val_dt: Optional[str] = None,
    enum_val_id: Optional[int] = None,
    service: PositionParameterService = Depends(get_service),
):
    try:
        service.write(
            position_id=position_id,
            parameter_id=parameter_id,
            val_real=val_real,
            val_int=val_int,
            val_str=val_str,
            val_dt=val_dt,
            enum_val_id=enum_val_id,
        )
        return MessageOut(detail="Значение параметра сохранено")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{position_id}")
def get_position_parameters(
    position_id: int,
    service: PositionParameterService = Depends(get_service),
):
    try:
        return service.get_for_position(position_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{position_id}/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position_parameter(
    position_id: int,
    parameter_id: int,
    service: PositionParameterService = Depends(get_service),
):
    try:
        service.delete(position_id, parameter_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
