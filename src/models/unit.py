from typing import List, Optional
from sqlalchemy import ForeignKey, String, Boolean, SmallInteger, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as SASession

from models.base import Base

class Unit(Base):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
