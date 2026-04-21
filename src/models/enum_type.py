from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

from models import Base


class EnumType(Base):
    __tablename__ = "enum_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    values = relationship(
        "EnumValue",
        back_populates="enum_type",
        cascade="all, delete"
    )
