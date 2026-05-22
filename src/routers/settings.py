from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_session
from services.settings_service import seed_db, clear_db
from schemas.common import MessageOut

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("/seed", response_model=MessageOut)
def seed(session: Session = Depends(get_session)):
    try:
        seed_db(session)
        return MessageOut(detail="Данные успешно загружены")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear", response_model=MessageOut)
def clear(session: Session = Depends(get_session)):
    try:
        clear_db(session)
        return MessageOut(detail="База данных очищена")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
