import asyncio
import logging

from app.domains.ticket.application.port.performance_link_query_port import PerformanceLinkQueryPort
from app.domains.ticket.application.port.ticket_crawl_port import TicketCrawlPort
from app.domains.ticket.application.port.ticket_repository_port import TicketRepositoryPort
from app.domains.ticket.application.port.ticket_search_port import TicketSearchPort
from app.domains.ticket.domain.service.performance_matcher import MatchCandidate, PerformanceMatcher

logger = logging.getLogger(__name__)


class SyncTicketsUseCase:

    def __init__(
        self,
        ticket_repo: TicketRepositoryPort,
        ticket_crawl: TicketCrawlPort,
        link_query: PerformanceLinkQueryPort,
        crawl_delay: float = 2.0,
        ticket_search: TicketSearchPort | None = None,
        matcher: PerformanceMatcher | None = None,
        search_batch_limit: int = 50,
        search_delay: float = 3.0,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._ticket_crawl = ticket_crawl
        self._link_query = link_query
        self._crawl_delay = crawl_delay
        self._ticket_search = ticket_search
        self._matcher = matcher
        self._search_batch_limit = search_batch_limit
        self._search_delay = search_delay

    async def execute(self) -> int:
        count = await self._sync_from_relates()

        if self._ticket_search and self._matcher:
            count += await self._sync_from_search()

        return count

    async def _sync_from_relates(self) -> int:
        """Phase 1: relates 기반 크롤링 (기존 로직)."""
        links = await self._link_query.fetch_all_booking_links()
        success_count = 0

        for item in links:
            mt20id = item["mt20id"]
            relates = item.get("relates", [])

            for relate in relates:
                vendor_name = relate.get("name", "")
                url = relate.get("url", "")
                if not url:
                    continue

                try:
                    ticket_info = await self._ticket_crawl.crawl(vendor_name, url, mt20id)
                    if ticket_info is not None:
                        await self._ticket_repo.save(ticket_info)
                        success_count += 1
                        logger.info("크롤링 성공: %s - %s", mt20id, vendor_name)
                except Exception:
                    logger.exception("크롤링 실패: %s - %s (%s)", mt20id, vendor_name, url)

                await asyncio.sleep(self._crawl_delay)

        logger.info("Phase 1 (relates) 완료: %d건 성공", success_count)
        return success_count

    async def _sync_from_search(self) -> int:
        """Phase 2: 검색 기반 크롤링 (relates 없는 공연 대상)."""
        assert self._ticket_search is not None
        assert self._matcher is not None

        performances = await self._link_query.fetch_performances_without_links()
        success_count = 0

        # 이미 ticket_infos에 데이터가 있는 공연은 스킵하기 위해 조회
        processed = 0
        for perf in performances:
            if processed >= self._search_batch_limit:
                logger.info("검색 배치 제한 도달: %d건", self._search_batch_limit)
                break

            mt20id = perf["mt20id"]
            prfnm = perf["prfnm"]

            # 이미 데이터가 있으면 스킵
            existing = await self._ticket_repo.find_by_mt20id(mt20id)
            if existing:
                continue

            processed += 1

            # 검색 쿼리 정제 (괄호, 특수문자 제거)
            search_query = self._matcher.extract_search_query(prfnm)
            if not search_query:
                continue

            try:
                search_results = await self._ticket_search.search(search_query)
            except Exception:
                logger.exception("검색 실패: %s (%s)", mt20id, prfnm)
                await asyncio.sleep(self._search_delay)
                continue

            if not search_results:
                logger.debug("검색 결과 없음: %s (%s)", mt20id, prfnm)
                await asyncio.sleep(self._search_delay)
                continue

            # 검색 결과를 MatchCandidate로 변환하여 매칭
            candidates = [
                MatchCandidate(title=sr.title, url=sr.url)
                for sr in search_results
            ]
            best = self._matcher.find_best_match(prfnm, candidates)

            if best is None:
                logger.debug("매칭 실패: %s (%s)", mt20id, prfnm)
                await asyncio.sleep(self._search_delay)
                continue

            # 매칭된 검색 결과의 vendor_name 찾기
            matched_sr = next(
                (sr for sr in search_results if sr.url == best.url), None,
            )
            vendor_name = matched_sr.vendor_name if matched_sr else "unknown"

            try:
                ticket_info = await self._ticket_crawl.crawl(
                    vendor_name, best.url, mt20id,
                )
                if ticket_info is not None:
                    await self._ticket_repo.save(ticket_info)
                    success_count += 1
                    logger.info(
                        "검색 크롤링 성공: %s - %s (%s)", mt20id, vendor_name, prfnm,
                    )
            except Exception:
                logger.exception(
                    "검색 크롤링 실패: %s - %s (%s)", mt20id, vendor_name, best.url,
                )

            await asyncio.sleep(self._search_delay)

        logger.info("Phase 2 (검색) 완료: %d건 성공", success_count)
        return success_count
