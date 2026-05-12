from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, SmallInteger, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as SASession

from models.base import Base
from models.position_parameter import PositionParameter


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # === УДАЛИТЬ старые hardcoded поля ===
    # weight, calories, protein, fat, carbs, is_liquid, is_hot, weight_unit_id

    category = relationship("Category", back_populates="positions")
    
    # Новая связь
    parameters: Mapped[list[PositionParameter]] = relationship(
        "PositionParameter", 
        back_populates="position",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Position(id={self.id!r}, name={self.name!r}, category_id={self.category_id!r})"
