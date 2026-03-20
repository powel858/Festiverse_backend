import asyncio
import logging
from datetime import datetime, timedelta

from app.domains.performance.application.port.kopis_api_port import KopisApiPort
from app.domains.performance.application.port.performance_repository_port import PerformanceRepositoryPort
from app.domains.performance.domain.entity.performance import Performance
from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

FESTIVAL_KEYWORD = "페스티벌"
DETAIL_CONCURRENCY = 1
DETAIL_DELAY = 0.2


class SyncPerformancesUseCase:

    def __init__(
        self,
        performance_repo: PerformanceRepositoryPort,
        kopis_api: KopisApiPort,
    ) -> None:
        self._performance_repo = performance_repo
        self._kopis_api = kopis_api

    async def execute(self) -> int:
        """KOPIS API에서 대중음악 공연 + '페스티벌' 키워드 축제를 수집하여 DB에 저장."""
        now = datetime.utcnow()
        stdate = (now - timedelta(days=31)).strftime("%Y%m%d")
        eddate = (now + timedelta(days=31)).strftime("%Y%m%d")
        genre = settings.DEFAULT_GENRE  # CCCD (대중음악)

        all_performances: list[Performance] = []

        # 대중음악 공연 목록 수집
        all_performances.extend(
            await self._fetch_all_pages(stdate, eddate, is_festival=False, shcate=genre)
        )
        # '페스티벌' 키워드 축제 목록 수집
        all_performances.extend(
            await self._fetch_all_pages(stdate, eddate, is_festival=True, shcate=genre, keyword=FESTIVAL_KEYWORD)
        )

        # 각 공연의 상세 정보(예매처 등)를 조회하여 병합
        all_performances = await self._enrich_with_details(all_performances)

        if all_performances:
            for p in all_performances:
                p.updated_at = now
            await self._performance_repo.save_many(all_performances)

        logger.info("배치 수집 완료: %d건 (장르: %s)", len(all_performances), genre)
        return len(all_performances)

    async def _enrich_with_details(
        self, performances: list[Performance],
    ) -> list[Performance]:
        """목록에서 수집한 공연들에 대해 상세 API를 순차 호출하여 예매처 등 상세 정보를 병합."""
        results: list[Performance] = []
        success_count = 0
        for perf in performances:
            detail = await self._kopis_api.fetch_performance_detail(perf.mt20id)
            if detail is not None:
                results.append(detail)
                success_count += 1
            else:
                results.append(perf)
            await asyncio.sleep(DETAIL_DELAY)
        logger.info("상세 정보 조회 완료: %d건 중 %d건 성공",
                     len(performances), success_count)
        return results

    async def _fetch_all_pages(
        self,
        stdate: str,
        eddate: str,
        is_festival: bool,
        shcate: str | None = None,
        keyword: str | None = None,
    ) -> list[Performance]:
        results: list[Performance] = []
        cpage = 1
        while True:
            if is_festival:
                batch = await self._kopis_api.fetch_festival_list(
                    stdate=stdate, eddate=eddate, cpage=cpage, rows=100, shcate=shcate,
                )
            else:
                batch = await self._kopis_api.fetch_performance_list(
                    stdate=stdate, eddate=eddate, cpage=cpage, rows=100,
                    shcate=shcate, shprfnm=keyword,
                )
            results.extend(batch)
            if len(batch) < 100:
                break
            cpage += 1
        return results
