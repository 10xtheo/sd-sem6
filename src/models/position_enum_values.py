from sqlalchemy import Table, Column, Integer, ForeignKey
from models import Base

position_enum_values = Table(
    "position_enum_values",
    Base.metadata,
    Column("position_id", ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True),
    Column("enum_value_id", ForeignKey("enum_values.id", ondelete="CASCADE"), primary_key=True),
)
