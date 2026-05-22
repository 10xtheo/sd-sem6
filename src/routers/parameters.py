from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from services.parameter_service import ParameterService
from schemas.parameter import ParameterCreate, ParameterOut

router = APIRouter(prefix="/parameters", tags=["parameters"])


def get_service(session: Session = Depends(get_session)) -> ParameterService:
    return ParameterService(session)


@router.get("/", response_model=List[ParameterOut])
def get_all_parameters(service: ParameterService = Depends(get_service)):
    return service.get_all()


@router.get("/{param_id}", response_model=ParameterOut)
def get_parameter(param_id: int, service: ParameterService = Depends(get_service)):
    try:
        return service.get_by_id(param_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ParameterOut, status_code=201)
def create_parameter(body: ParameterCreate, service: ParameterService = Depends(get_service)):
    try:
        return service.create(
            short_name=body.short_name,
            name=body.name,
            param_type_code=body.param_type_code,
            enum_type_id=body.enum_type_id,
            unit_id=body.unit_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{param_id}", status_code=204)
def delete_parameter(param_id: int, service: ParameterService = Depends(get_service)):
    try:
        service.delete(param_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
