from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import InternalError

from database import get_session
from repository.parameter_repository import ParameterRepository
from schemas.parameter import ParameterCreate, ParameterOut, ParameterUpdate

router = APIRouter(prefix="/parameters", tags=["parameters"])


def get_repo(session: Session = Depends(get_session)) -> ParameterRepository:
    return ParameterRepository(session)

# Процедура INS_PARAMETER СЕРВЕР
@router.post("/", response_model=ParameterOut, status_code=201)
def create_parameter(body: ParameterCreate, repo: ParameterRepository = Depends(get_repo)):
    try:
        return repo.add_parameter(
            short_name=body.short_name,
            name=body.name,
            param_type_code=body.param_type_code,
            enum_type_id=body.enum_type_id,
            unit_id=body.unit_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.get("/", response_model=List[ParameterOut])
def get_all_parameters(repo: ParameterRepository = Depends(get_repo)):
    return repo.get_all()


@router.get("/{param_id}", response_model=ParameterOut)
def get_parameter(param_id: int, repo: ParameterRepository = Depends(get_repo)):
    param = repo.get_by_id(param_id)
    if not param:
        raise HTTPException(status_code=404, detail="Параметр не найден")
    return param


@router.patch("/{param_id}", response_model=ParameterOut)
def update_parameter(param_id: int, data: ParameterUpdate, repo: ParameterRepository = Depends(get_repo)):
    # Можно добавить метод update в репозиторий позже
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{param_id}", status_code=204)
def delete_parameter(param_id: int, repo: ParameterRepository = Depends(get_repo)):
    try:
        repo.delete_parameter(param_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
