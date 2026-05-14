from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_session
from repository.category_parameter_repository import CategoryParameterRepository
from schemas.category_parameter import CategoryParameterCreate, CategoryParameterOut

router = APIRouter(prefix="/category-parameters", tags=["category-parameters"])


def get_repo(session: Session = Depends(get_session)) -> CategoryParameterRepository:
    return CategoryParameterRepository(session)

# Процедура ADD_PARAMETR_CLASS СЕРВЕР
@router.post("/", status_code=201)
def add_parameter_to_category(
    data: CategoryParameterCreate, 
    repo: CategoryParameterRepository = Depends(get_repo)
):
    try:
        repo.add_to_category(
            category_id=data.category_id,
            parameter_id=data.parameter_id,
            order_num=data.order_num,
            min_val=data.min_val,
            max_val=data.max_val
        )
        return {"detail": "Параметр успешно добавлен к категории и всем дочерним"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Процедура FIND_PAR_CLASS сервер
@router.get("/category/{category_id}", response_model=list[CategoryParameterOut])
def get_category_parameters(category_id: int, repo: CategoryParameterRepository = Depends(get_repo)):
    return repo.get_for_category(category_id)

@router.delete("/{category_id}/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter_from_category(
    category_id: int,
    parameter_id: int,
    repo: CategoryParameterRepository = Depends(get_repo)
):
    """
    Удаляет параметр у категории и всех её потомков (каскадно).
    """
    try:
        # Проверяем, существует ли параметр у категории
        if not repo.parameter_exists_in_category(category_id, parameter_id):
            raise HTTPException(
                status_code=404,
                detail=f"Параметр {parameter_id} не найден у категории {category_id}"
            )
        
        deleted_count = repo.delete_from_category(category_id, parameter_id)
        
        return None  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
