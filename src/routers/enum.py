from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_session
from services.enum_service import EnumService
from schemas.enum_type import EnumTypeCreate, EnumTypeUpdate, EnumTypeOut
from schemas.enum_value import EnumValueCreate, EnumValueUpdate, EnumValueOut
from schemas.enum_validate import EnumValidateIn
from schemas.common import MessageOut

router = APIRouter(prefix="/enum", tags=["enum"])


def get_service(session: Session = Depends(get_session)) -> EnumService:
    return EnumService(session)


@router.get("/types", response_model=list[EnumTypeOut])
def get_enum_types(service: EnumService = Depends(get_service)):
    return service.get_all_types()


@router.get("/types/{type_id}", response_model=EnumTypeOut)
def get_enum_type(type_id: int, service: EnumService = Depends(get_service)):
    try:
        return service.get_type(type_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/types/{type_id}/values", response_model=list[EnumValueOut])
def get_enum_values_by_type(
    type_id: int,
    desc: bool = Query(False),
    service: EnumService = Depends(get_service),
):
    return service.get_values_by_type(type_id, desc)


@router.post("/types", response_model=EnumTypeOut)
def create_enum_type(data: EnumTypeCreate, service: EnumService = Depends(get_service)):
    return service.create_type(data.model_dump())


@router.patch("/types/{type_id}", response_model=EnumTypeOut)
def update_enum_type(type_id: int, data: EnumTypeUpdate, service: EnumService = Depends(get_service)):
    try:
        return service.update_type(type_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/types/{type_id}", response_model=MessageOut)
def delete_enum_type(type_id: int, service: EnumService = Depends(get_service)):
    try:
        service.delete_type(type_id)
        return MessageOut(detail="deleted")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/values", response_model=list[EnumValueOut])
def get_enum_values(service: EnumService = Depends(get_service)):
    return service.get_all_values()


@router.get("/values/{value_id}", response_model=EnumValueOut)
def get_enum_value(value_id: int, service: EnumService = Depends(get_service)):
    try:
        return service.get_value(value_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/values", response_model=EnumValueOut)
def create_enum_value(data: EnumValueCreate, service: EnumService = Depends(get_service)):
    return service.create_value(data.model_dump())


@router.patch("/values/{value_id}", response_model=EnumValueOut)
def update_enum_value(value_id: int, data: EnumValueUpdate, service: EnumService = Depends(get_service)):
    try:
        return service.update_value(value_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/values/{value_id}", response_model=MessageOut)
def delete_enum_value(value_id: int, service: EnumService = Depends(get_service)):
    try:
        service.delete_value(value_id)
        return MessageOut(detail="deleted")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/validate")
def validate_enum_value(body: EnumValidateIn, service: EnumService = Depends(get_service)):
    try:
        value = service.validate(body.type_code, body.value)
        return {"valid": True, "id": value.id, "name": value.name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
