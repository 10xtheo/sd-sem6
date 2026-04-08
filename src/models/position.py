from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, SmallInteger, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as SASession

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
