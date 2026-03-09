from typing import List, Optional, Sequence
from sqlalchemy import ForeignKey, String, Integer, Boolean, Text, Index, SmallInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Session as SASession
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

    