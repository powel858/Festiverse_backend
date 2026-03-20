import logging

from app.domains.ticket.adapter.outbound.external.searchers.base_searcher import BaseSearcher
from app.domains.ticket.application.port.ticket_search_port import SearchResult, TicketSearchPort

logger = logging.getLogger(__name__)


class TicketSearchAdapter(TicketSearchPort):

    def __init__(self, searchers: list[BaseSearcher]) -> None:
        self._searchers = searchers

    async def search(self, query: str) -> list[SearchResult]:
        results: list[SearchResult] = []
        for searcher in self._searchers:
            try:
                found = await searcher.search(query)
                results.extend(found)
                logger.debug(
                    "%s 검색 결과: %d건 (%s)",
                    searcher.vendor_name, len(found), query,
                )
            except Exception:
                logger.exception("%s 검색 중 오류: %s", searcher.vendor_name, query)
        return results
