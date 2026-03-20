from fastapi import APIRouter, Depends, HTTPException, Query

from app.domains.performance.adapter.outbound.external.kopis_api_adapter import KopisApiAdapter
from app.domains.performance.adapter.outbound.persistence.performance_repository import PerformanceRepository
from app.domains.performance.adapter.outbound.persistence.venue_repository import VenueRepository
from app.domains.ticket.adapter.outbound.persistence.ticket_repository import TicketRepository
from app.domains.performance.application.request.list_festivals_request import ListFestivalsRequest
from app.domains.performance.application.request.list_performances_request import ListPerformancesRequest
from app.domains.performance.application.response.festival_summary_response import FestivalSummaryResponse
from app.domains.performance.application.response.performance_detail_response import PerformanceDetailResponse
from app.domains.performance.application.response.performance_summary_response import PerformanceSummaryResponse
from app.domains.performance.application.usecase.get_performance_detail_usecase import GetPerformanceDetailUseCase
from app.domains.performance.application.usecase.list_festivals_usecase import ListFestivalsUseCase
from app.domains.performance.application.usecase.list_performances_usecase import ListPerformancesUseCase
from app.infrastructure.config.settings import settings
from app.infrastructure.database.session import async_session_factory
from app.infrastructure.external.http_client import get_http_client

router = APIRouter(prefix="/api", tags=["performances"])


async def _get_list_performances_usecase():
    async with async_session_factory() as session:
        yield ListPerformancesUseCase(PerformanceRepository(session))


async def _get_detail_usecase():
    client = await get_http_client()
    kopis_api = KopisApiAdapter(client, settings.KOPIS_BASE_URL, settings.KOPIS_API_KEY)
    async with async_session_factory() as session:
        yield GetPerformanceDetailUseCase(
            PerformanceRepository(session),
            VenueRepository(session),
            kopis_api,
            TicketRepository(session),
        )


async def _get_list_festivals_usecase():
    async with async_session_factory() as session:
        yield ListFestivalsUseCase(PerformanceRepository(session))


@router.get("/performances", response_model=list[PerformanceSummaryResponse])
async def list_performances(
    stdate: str | None = Query(None, description="시작일 (YYYYMMDD)"),
    eddate: str | None = Query(None, description="종료일 (YYYYMMDD)"),
    genre: str | None = Query(None, description="장르코드"),
    region: str | None = Query(None, description="지역코드"),
    keyword: str | None = Query(None, description="검색 키워드"),
    state: str | None = Query(None, description="공연상태 (01/02/03)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    usecase: ListPerformancesUseCase = Depends(_get_list_performances_usecase),
) -> list[PerformanceSummaryResponse]:
    request = ListPerformancesRequest(
        stdate=stdate, eddate=eddate, genre=genre,
        region=region, keyword=keyword, state=state,
        page=page, size=size,
    )
    return await usecase.execute(request)


@router.get("/performances/{mt20id}", response_model=PerformanceDetailResponse)
async def get_performance_detail(
    mt20id: str,
    usecase: GetPerformanceDetailUseCase = Depends(_get_detail_usecase),
) -> PerformanceDetailResponse:
    result = await usecase.execute(mt20id)
    if result is None:
        raise HTTPException(status_code=404, detail="공연을 찾을 수 없습니다.")
    return result


@router.get("/festivals", response_model=list[FestivalSummaryResponse])
async def list_festivals(
    stdate: str | None = Query(None, description="시작일 (YYYYMMDD)"),
    eddate: str | None = Query(None, description="종료일 (YYYYMMDD)"),
    genre: str | None = Query(None, description="장르코드"),
    keyword: str | None = Query(None, description="검색 키워드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    usecase: ListFestivalsUseCase = Depends(_get_list_festivals_usecase),
) -> list[FestivalSummaryResponse]:
    request = ListFestivalsRequest(
        stdate=stdate, eddate=eddate, genre=genre,
        keyword=keyword, page=page, size=size,
    )
    return await usecase.execute(request)
