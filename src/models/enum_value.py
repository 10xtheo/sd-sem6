from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, Float, ForeignKey

from models.base import Base


class EnumValue(Base):
    __tablename__ = "enum_values"

    id: Mapped[int] = mapped_column(primary_key=True)

    enum_type_id: Mapped[int] = mapped_column(
        ForeignKey("enum_types.id", ondelete="CASCADE"),
        nullable=False
    )

    order_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50))
    numeric_value: Mapped[float | None] = mapped_column(Float)

    unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id", ondelete="SET NULL"),
        nullable=True
    )

    # Только связь с типом
    enum_type = relationship("EnumType", back_populates="values")

    def __repr__(self):
        return f"EnumValue(id={self.id}, name={self.name!r}, code={self.code})"
