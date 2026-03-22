from typing import Any

from pydantic import BaseModel


class DashboardRow(BaseModel):
    """대시보드 View 조회 결과의 단일 행. 컬럼이 View마다 다르므로 dict 기반."""
    model_config = {"extra": "allow"}


class DashboardResponse(BaseModel):
    view_name: str
    rows: list[dict[str, Any]]
    total: int
