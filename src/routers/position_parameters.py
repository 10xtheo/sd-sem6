from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_session
from repository.position_parameter_repository import PositionParameterRepository

router = APIRouter(prefix="/position-parameters", tags=["position-parameters"])


def get_repo(session: Session = Depends(get_session)) -> PositionParameterRepository:
    return PositionParameterRepository(session)

# Процедура WRITE_PAR_PROD СЕРВВЕР
@router.post("/{position_id}/parameters/{parameter_id}")
def write_position_parameter(
    position_id: int,
    parameter_id: int,
    val_real: Optional[float] = None,
    val_int: Optional[int] = None,
    val_str: Optional[str] = None,
    val_dt: Optional[str] = None,
    enum_val_id: Optional[int] = None,
    repo: PositionParameterRepository = Depends(get_repo)
):
    try:
        repo.write_value(
            position_id=position_id,
            parameter_id=parameter_id,
            val_real=val_real,
            val_int=val_int,
            val_str=val_str,
            val_dt=val_dt,
            enum_val_id=enum_val_id
        )
        return {"detail": "Значение параметра сохранено"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{position_id}")
def get_position_parameters(position_id: int, repo: PositionParameterRepository = Depends(get_repo)):
    """Получить все параметры позиции"""
    return repo.get_for_position(position_id)
