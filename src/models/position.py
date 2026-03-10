from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import Session as SASession
from sqlalchemy import select

from models.base import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[Optional[int]] = mapped_column(SmallInteger)
    calories: Mapped[Optional[int]] = mapped_column(SmallInteger)
    protein: Mapped[Optional[int]] = mapped_column(SmallInteger)
    fat: Mapped[Optional[int]] = mapped_column(SmallInteger)
    carbs: Mapped[Optional[int]] = mapped_column(SmallInteger)
    is_liquid: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hot: Mapped[bool] = mapped_column(Boolean, default=False)

    category = relationship("Category", back_populates="positions")

    def __repr__(self) -> str:
        return f"Position(id={self.id!r}, name={self.name!r}, category_id={self.category_id!r})"

    @classmethod
    def get_by_id(cls, session: SASession, id: int) -> Optional["Position"]:
        return session.get(cls, id)

    @classmethod
    def get_by_category(cls, session: SASession, category_id: int) -> List["Position"]:
        return list(session.execute(
            select(cls).where(cls.category_id == category_id).order_by(cls.id)
        ).scalars().all())
    
    @classmethod
    def get_all(cls, session: SASession) -> List["Position"]:
        return list(session.execute(select(cls)).scalars().all())

    @classmethod
    def search_by_name(cls, session: SASession, name_pattern: str) -> List["Position"]:
        return list(session.execute(
            select(cls).where(cls.name.ilike(f"%{name_pattern}%"))
        ).scalars().all())
