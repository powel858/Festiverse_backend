import json
import logging

import httpx
from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.searchers.base_searcher import BaseSearcher
from app.domains.ticket.application.port.ticket_search_port import SearchResult

logger = logging.getLogger(__name__)

_BASE_URL = "https://tickets.interpark.com"
_SEARCH_URL = f"{_BASE_URL}/search"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class InterparkSearcher(BaseSearcher):

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    @property
    def vendor_name(self) -> str:
        return "인터파크"

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
            logger.warning("인터파크 검색 실패: %s", query)
            return []

        return self._parse_results(resp.text)

    @staticmethod
    def _parse_results(html: str) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchResult] = []

        # Next.js __NEXT_DATA__ JSON에서 검색 결과 추출
        script = soup.select_one("script#__NEXT_DATA__")
        if not script or not script.string:
            return results

        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            return results

        docs = (
            data.get("props", {})
            .get("pageProps", {})
            .get("searchResult", {})
            .get("goods", {})
            .get("docs", [])
        )

        for doc in docs:
            goods_name = doc.get("goodsName", "")
            goods_code = doc.get("goodsCode", "")
            if not goods_name or not goods_code:
                continue

            url = f"{_BASE_URL}/goods/{goods_code}"
            results.append(SearchResult(
                title=goods_name,
                url=url,
                vendor_name="인터파크",
            ))

        return results
