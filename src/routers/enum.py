from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_session
from repository.enum_repository import EnumRepository
from schemas.enum_type import (
    EnumTypeCreate,
    EnumTypeUpdate,
    EnumTypeOut,
)
from schemas.enum_value import (
    EnumValueCreate,
    EnumValueUpdate,
    EnumValueOut,
)

from schemas.enum_validate import EnumValidateIn

router = APIRouter(prefix="/enum", tags=["enum"])


def get_repo(session: Session = Depends(get_session)) -> EnumRepository:
    return EnumRepository(session)


@router.post("/types", response_model=EnumTypeOut)
def create_enum_type(data: EnumTypeCreate, repo: EnumRepository = Depends(get_repo)):
    return repo.create_enum_type(data.model_dump())

@router.get("/types", response_model=list[EnumTypeOut])
def get_enum_types(repo: EnumRepository = Depends(get_repo)):
    return repo.get_enum_types()

@router.get("/types/{type_id}", response_model=EnumTypeOut)
def get_enum_type(type_id: int, repo: EnumRepository = Depends(get_repo)):
    obj = repo.get_enum_type(type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Enum type not found")
    return obj

@router.get("/types/{type_id}/values", response_model=list[EnumValueOut])
def get_enum_values_by_type(
    type_id: int,
    desc: bool = Query(False, description="Sort descending if true"),
    repo: EnumRepository = Depends(get_repo),
):
    try:
        return repo.get_enum_values_by_type(type_id, desc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/types/{type_id}", response_model=EnumTypeOut)
def update_enum_type(
    type_id: int,
    data: EnumTypeUpdate,
    repo: EnumRepository = Depends(get_repo),
):
    obj = repo.update_enum_type(type_id, data.model_dump())
    if not obj:
        raise HTTPException(status_code=404, detail="Enum type not found")
    return obj

@router.delete("/types/{type_id}")
def delete_enum_type(type_id: int, repo: EnumRepository = Depends(get_repo)):
    if not repo.delete_enum_type(type_id):
        raise HTTPException(status_code=404, detail="Enum type not found")
    return {"detail": "deleted"}



@router.post("/values", response_model=EnumValueOut)
def create_enum_value(data: EnumValueCreate, repo: EnumRepository = Depends(get_repo)):
    return repo.create_enum_value(data.model_dump())

@router.get("/values", response_model=list[EnumValueOut])
def get_enum_values(repo: EnumRepository = Depends(get_repo)):
    return repo.get_enum_values()

@router.get("/values/{value_id}", response_model=EnumValueOut)
def get_enum_value(value_id: int, repo: EnumRepository = Depends(get_repo)):
    obj = repo.get_enum_value(value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Enum value not found")
    return obj

@router.patch("/values/{value_id}", response_model=EnumValueOut)
def update_enum_value(
    value_id: int,
    data: EnumValueUpdate,
    repo: EnumRepository = Depends(get_repo),
):
    obj = repo.update_enum_value(value_id, data.model_dump())
    if not obj:
        raise HTTPException(status_code=404, detail="Enum value not found")
    return obj

@router.delete("/values/{value_id}")
def delete_enum_value(value_id: int, repo: EnumRepository = Depends(get_repo)):
    if not repo.delete_enum_value(value_id):
        raise HTTPException(status_code=404, detail="Enum value not found")
    return {"detail": "deleted"}

@router.post("/validate")
def validate_enum_value(
    body: EnumValidateIn,
    repo: EnumRepository = Depends(get_repo),
):
    try:
        value = repo.validate_value_in_type(
            body.type_code,
            body.value
        )

        return {
            "valid": True,
            "id": value.id,
            "name": value.name,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
