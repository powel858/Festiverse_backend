import logging
import re

import httpx
from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.searchers.base_searcher import BaseSearcher
from app.domains.ticket.application.port.ticket_search_port import SearchResult

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.ticketlink.co.kr"
_SEARCH_URL = f"{_BASE_URL}/search"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class TicketlinkSearcher(BaseSearcher):

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    @property
    def vendor_name(self) -> str:
        return "티켓링크"

    async def search(self, query: str) -> list[SearchResult]:
        try:
            resp = await self._client.get(
                _SEARCH_URL,
                params={"keyword": query},
                headers={"User-Agent": _USER_AGENT},
                follow_redirects=True,
                timeout=15.0,
            )
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("티켓링크 검색 실패: %s", query)
            return []

        return self._parse_results(resp.text)

    @staticmethod
    def _parse_results(html: str) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        # 검색 결과에서 공연 상세 링크 추출
        # 티켓링크 공연 상세 URL 패턴: /product/{id} 또는 /event/{id}
        for a_tag in soup.select("a[href]"):
            href = str(a_tag.get("href", ""))

            # 공연 상세 페이지 링크만 필터링
            match = re.search(r"/(product|event|performance)/(\d+)", href)
            if not match:
                continue

            title = a_tag.get_text(strip=True)
            if not title:
                # 인접 텍스트 요소에서 제목 추출 시도
                parent = a_tag.parent
                if parent:
                    title = parent.get_text(strip=True)
            if not title:
                continue

            # 상대 경로를 절대 경로로 변환
            if href.startswith("/"):
                url = f"{_BASE_URL}{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = f"{_BASE_URL}/{href}"

            # 중복 URL 방지
            if not any(r.url == url for r in results):
                results.append(SearchResult(
                    title=title,
                    url=url,
                    vendor_name="티켓링크",
                ))

        return results
