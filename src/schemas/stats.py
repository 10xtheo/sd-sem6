from typing import List, Optional
from pydantic import BaseModel


class StatsSummary(BaseModel):
    categories_total: int
    categories_root: int
    positions_total: int


class StatsByCategory(BaseModel):
    id: int
    name: str
    children_count: int
    positions_count: int


class IntegrityIssue(BaseModel):
    type: str
    category_id: Optional[int] = None
    position_id: Optional[int] = None
    parent_id: Optional[int] = None


class IntegrityReport(BaseModel):
    ok: bool
    issues: List[IntegrityIssue]
