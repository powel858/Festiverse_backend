import re

import httpx

from app.domains.blog.application.port.blog_search_port import BlogSearchPort
from app.domains.blog.domain.entity.blog_post import BlogPost

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text)


class NaverBlogAdapter(BlogSearchPort):

    def __init__(self, client: httpx.AsyncClient, client_id: str, client_secret: str) -> None:
        self._client = client
        self._client_id = client_id
        self._client_secret = client_secret

    async def search(self, query: str, display: int = 3) -> list[BlogPost]:
        resp = await self._client.get(
            "https://openapi.naver.com/v1/search/blog.json",
            headers={
                "X-Naver-Client-Id": self._client_id,
                "X-Naver-Client-Secret": self._client_secret,
            },
            params={"query": query, "display": display, "sort": "sim"},
        )
        resp.raise_for_status()
        data = resp.json()

        return [
            BlogPost(
                title=_strip_html(item.get("title", "")),
                link=item.get("link", ""),
                description=_strip_html(item.get("description", "")),
                bloggername=item.get("bloggername", ""),
                postdate=item.get("postdate", ""),
            )
            for item in data.get("items", [])
        ]
