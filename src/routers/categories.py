from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from repository import CategoryRepository
from schemas import CategoryCreate, CategoryUpdate, CategoryMove, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


def get_repo(session: Session = Depends(get_session)) -> CategoryRepository:
    return CategoryRepository(session)


@router.get("/", response_model=List[CategoryOut])
def list_categories(repo: CategoryRepository = Depends(get_repo)):
    return repo.get_all_categories()


@router.get("/tree")
def get_tree(start_id: Optional[int] = None, repo: CategoryRepository = Depends(get_repo)):
    items = repo.get_tree(start_category_id=start_id)
    return [
        {"type": t, "id": obj.id, "name": obj.name, "level": level}
        for t, obj, level in items
    ]


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, repo: CategoryRepository = Depends(get_repo)):
    category = repo.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.get("/{category_id}/children", response_model=List[CategoryOut])
def get_children(category_id: int, session: Session = Depends(get_session), repo: CategoryRepository = Depends(get_repo)):
    category = repo.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category.get_children(session)


@router.get("/{category_id}/descendants", response_model=List[CategoryOut])
def get_descendants(category_id: int, session: Session = Depends(get_session), repo: CategoryRepository = Depends(get_repo)):
    category = repo.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category.get_all_descendants(session)


@router.get("/{category_id}/parents", response_model=List[CategoryOut])
def get_parents(category_id: int, repo: CategoryRepository = Depends(get_repo)):
    category = repo.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return repo.get_all_parents(category)


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(body: CategoryCreate, repo: CategoryRepository = Depends(get_repo)):
    return repo.add_category(name=body.name, parent_id=body.parent_id)


@router.patch("/{category_id}", response_model=CategoryOut)
def rename_category(category_id: int, body: CategoryUpdate, repo: CategoryRepository = Depends(get_repo)):
    ok, message, category = repo.update_category(category_id, name=body.name)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return category


@router.patch("/{category_id}/move", response_model=CategoryOut)
def move_category(category_id: int, body: CategoryMove, repo: CategoryRepository = Depends(get_repo)):
    try:
        return repo.move_category(category_id, body.new_parent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, cascade: bool = False, repo: CategoryRepository = Depends(get_repo)):
    try:
        repo.delete_category(category_id, cascade=cascade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
