import logging
import re
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.searchers.base_searcher import BaseSearcher
from app.domains.ticket.application.port.ticket_search_port import SearchResult

logger = logging.getLogger(__name__)

_BASE_URL = "https://ticket.melon.com"
_SEARCH_URL = f"{_BASE_URL}/search/ajax/listPerformance.htm"
_DETAIL_URL = f"{_BASE_URL}/performance/index.htm"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class MelonSearcher(BaseSearcher):

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    @property
    def vendor_name(self) -> str:
        return "멜론티켓"

    async def search(self, query: str) -> list[SearchResult]:
        try:
            resp = await self._client.get(
                _SEARCH_URL,
                params={"q": query},
                headers={"User-Agent": _USER_AGENT},
                follow_redirects=True,
                timeout=15.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("멜론티켓 검색 실패: %s", query)
            return []

        return self._parse_results(resp.text)

    @staticmethod
    def _parse_results(html: str) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        for a_tag in soup.select("a[href*='prodId=']"):
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if not title or not href:
                continue

            # prodId 추출하여 전체 URL 생성
            match = re.search(r"prodId=(\d+)", str(href))
            if match:
                prod_id = match.group(1)
                url = f"{_DETAIL_URL}?prodId={prod_id}"
                results.append(SearchResult(
                    title=title,
                    url=url,
                    vendor_name="멜론티켓",
                ))

        return results
