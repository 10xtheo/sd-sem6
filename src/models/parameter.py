from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Float, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.enum_type import EnumType
from models.enum_value import EnumValue
from models.unit import Unit


class Parameter(Base):
    """Справочник параметров (аналог метаданных)"""
    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(primary_key=True)

    short_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Тип параметра: real, integer, string, datetime, enum
    param_type_id: Mapped[int] = mapped_column(
        ForeignKey("enum_values.id", ondelete="RESTRICT"), nullable=False
    )

    # Для типа enum — ссылка на группу значений
    enum_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("enum_types.id", ondelete="RESTRICT"), nullable=True
    )

    # Единица измерения (для числовых параметров)
    unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"), nullable=True
    )

    # Связи
    param_type: Mapped["EnumValue"] = relationship("EnumValue", foreign_keys=[param_type_id])
    enum_type: Mapped[Optional["EnumType"]] = relationship("EnumType")
    unit: Mapped[Optional["Unit"]] = relationship("Unit")

    def __repr__(self):
        return f"Parameter(id={self.id}, short_name={self.short_name!r}, name={self.name!r})"
