from typing import Optional
from sqlalchemy import ForeignKey, Float, Integer as SqlInteger, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class PositionParameter(Base):
    """Значения параметров конкретной позиции"""
    __tablename__ = "position_parameters"

    position_id: Mapped[int] = mapped_column(
        ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True
    )
    parameter_id: Mapped[int] = mapped_column(
        ForeignKey("parameters.id", ondelete="CASCADE"), primary_key=True
    )

    val_real: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    val_int: Mapped[Optional[int]] = mapped_column(SqlInteger, nullable=True)
    val_str: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    val_dt: Mapped[Optional[str]] = mapped_column(TIMESTAMP, nullable=True)  # или DateTime
    enum_val_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("enum_values.id", ondelete="SET NULL"), nullable=True
    )

    # Связи
    position = relationship("Position", back_populates="parameters")
    parameter = relationship("Parameter")
    enum_value = relationship("EnumValue")

    def __repr__(self):
        return f"PositionParameter(pos={self.position_id}, param={self.parameter_id})"
