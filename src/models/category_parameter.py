from sqlalchemy import ForeignKey, Float, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from models.base import Base


class CategoryParameter(Base):
    """Параметры, привязанные к категории (с настройками мин/макс и порядком)"""
    __tablename__ = "category_parameters"

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    parameter_id: Mapped[int] = mapped_column(
        ForeignKey("parameters.id", ondelete="CASCADE"), primary_key=True
    )

    order_num: Mapped[int] = mapped_column(SmallInteger, default=0)
    min_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Связи
    category = relationship("Category", back_populates="parameters")
    parameter = relationship("Parameter")

    def __repr__(self):
        return f"CategoryParameter(cat={self.category_id}, param={self.parameter_id})"
