import logging

import httpx

from app.domains.ticket.adapter.outbound.external.parsers.base_parser import BaseParser
from app.domains.ticket.application.port.ticket_crawl_port import TicketCrawlPort
from app.domains.ticket.domain.entity.ticket_info import TicketInfo

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class TicketCrawlAdapter(TicketCrawlPort):

    def __init__(self, client: httpx.AsyncClient, parsers: list[BaseParser]) -> None:
        self._client = client
        self._parsers = parsers

    async def crawl(self, vendor_name: str, url: str, mt20id: str) -> TicketInfo | None:
        parser = self._find_parser(url)
        if parser is None:
            logger.debug("지원하지 않는 예매처: %s (%s)", vendor_name, url)
            return None

        try:
            resp = await self._client.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                follow_redirects=True,
                timeout=15.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("HTTP 요청 실패: %s", url)
            return None

        return parser.parse(resp.text, url, mt20id)

    def _find_parser(self, url: str) -> BaseParser | None:
        for parser in self._parsers:
            if parser.can_handle(url):
                return parser
        return None
