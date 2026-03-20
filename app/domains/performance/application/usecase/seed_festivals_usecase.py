import asyncio
import logging
from datetime import datetime

from app.domains.performance.application.port.kopis_api_port import KopisApiPort
from app.domains.performance.application.port.performance_repository_port import PerformanceRepositoryPort
from app.domains.performance.domain.entity.performance import Performance

logger = logging.getLogger(__name__)

DETAIL_DELAY = 0.2


class SeedFestivalsUseCase:
    """노션 페스티벌 리스트 기반으로 KOPIS API 검색 후 DB에 시드하는 UseCase."""

    def __init__(
        self,
        performance_repo: PerformanceRepositoryPort,
        kopis_api: KopisApiPort,
    ) -> None:
        self._performance_repo = performance_repo
        self._kopis_api = kopis_api

    async def execute(
        self,
        keywords: list[str],
        stdate: str = "20260301",
        eddate: str = "20261031",
    ) -> int:
        """키워드 리스트로 KOPIS 검색 → 상세 조회 → DB 저장.

        Args:
            keywords: KOPIS 검색용 키워드 리스트 (페스티벌명 또는 축약어)
            stdate: 검색 시작일 (YYYYMMDD)
            eddate: 검색 종료일 (YYYYMMDD)

        Returns:
            저장된 공연 수
        """
        now = datetime.utcnow()
        all_performances: list[Performance] = []
        seen_ids: set[str] = set()

        # 축제 목록은 한 번만 조회 (KOPIS rate limit 대응)
        logger.info("KOPIS 축제 목록 사전 조회 중...")
        fest_cache = await self._fetch_all_festivals(stdate, eddate)
        logger.info("축제 목록 %d건 캐싱 완료", len(fest_cache))

        for i, keyword in enumerate(keywords):
            logger.info("[%d/%d] KOPIS 검색: '%s'", i + 1, len(keywords), keyword)

            # 공연 목록 검색 (shprfnm 파라미터)
            results = await self._kopis_api.fetch_performance_list(
                stdate=stdate, eddate=eddate, shprfnm=keyword, rows=100,
            )

            # 캐싱된 축제 목록에서 키워드 매칭
            normalized_kw = keyword.replace(" ", "")
            for fr in fest_cache:
                if normalized_kw in fr.prfnm.replace(" ", ""):
                    results.append(fr)

            new_count = 0
            for perf in results:
                if perf.mt20id in seen_ids:
                    continue
                seen_ids.add(perf.mt20id)

                detail = await self._kopis_api.fetch_performance_detail(perf.mt20id)
                if detail:
                    detail.updated_at = now
                    all_performances.append(detail)
                else:
                    perf.updated_at = now
                    all_performances.append(perf)
                new_count += 1
                await asyncio.sleep(DETAIL_DELAY)

            logger.info("  → 검색 %d건, 신규 %d건", len(results), new_count)

        if all_performances:
            await self._performance_repo.save_many(all_performances)

        logger.info("시드 완료: 총 %d건 저장", len(all_performances))
        return len(all_performances)

    async def _fetch_all_festivals(
        self, stdate: str, eddate: str,
    ) -> list[Performance]:
        """축제 목록을 전체 페이지 조회."""
        results: list[Performance] = []
        cpage = 1
        while True:
            batch = await self._kopis_api.fetch_festival_list(
                stdate=stdate, eddate=eddate, cpage=cpage, rows=100,
            )
            results.extend(batch)
            if len(batch) < 100:
                break
            cpage += 1
        return results
