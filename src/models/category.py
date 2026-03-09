from typing import List, Optional, Sequence
from sqlalchemy import ForeignKey, String, Integer, Boolean, Text, Index, SmallInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Session as SASession
from sqlalchemy import select

from models.base import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    
    # relationships
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[List["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"

    @classmethod
    def get_by_id(cls, session: SASession, id: int) -> Optional["Category"]:
        """Получить категорию по ID"""
        return session.get(cls, id)

    @classmethod
    def get_all(cls, session: SASession) -> List["Category"]:
        """Получить все категории"""
        return list(session.execute(select(cls)).scalars().all())

    def get_children(self, session: SASession) -> List["Category"]:
        """Получить прямых потомков"""
        return list(session.execute(select(Category).where(Category.parent_id == self.id).order_by(Category.id)).scalars().all())

    def get_all_descendants(self, session: SASession) -> List["Category"]:
        """Получить всех потомков (рекурсивно)"""
        
        # Self-referential recursive query using ORM
        cte = select(Category).where(Category.id == self.id).cte(name="descendants", recursive=True)
        
        cte = cte.union_all(
            select(Category).join(cte, Category.parent_id == cte.c.id)
        )
        
        # Get all descendants excluding self
        result = list(session.execute(select(Category).from_statement(select(Category).where(Category.id.in_(select(cte.c.id).where(cte.c.id != self.id))))
        ).scalars().all())
        
        return result
