from pydantic import BaseModel, Field


class ListPerformancesRequest(BaseModel):
    stdate: str | None = Field(None, description="시작일 (YYYYMMDD)")
    eddate: str | None = Field(None, description="종료일 (YYYYMMDD)")
    genre: str | None = Field(None, description="장르코드")
    region: str | None = Field(None, description="지역코드")
    keyword: str | None = Field(None, description="검색 키워드")
    state: str | None = Field(None, description="공연상태 (01/02/03)")
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(20, ge=1, le=100, description="페이지 크기")
