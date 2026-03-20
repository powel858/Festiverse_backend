from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    vendor_name: str


class TicketSearchPort(ABC):

    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        """공연명으로 티켓 사이트를 검색하여 결과 목록을 반환한다."""
        ...
