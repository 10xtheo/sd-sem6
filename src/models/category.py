from typing import List, Optional
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as SASession

from models.base import Base
from models.category_parameter import CategoryParameter

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)

    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="category", cascade="all, delete-orphan")
    
    # В конец класса Category добавь:
    parameters: Mapped[list[CategoryParameter]] = relationship(
        "CategoryParameter",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"
