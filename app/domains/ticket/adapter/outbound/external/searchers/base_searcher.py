from abc import ABC, abstractmethod

from app.domains.ticket.application.port.ticket_search_port import SearchResult


class BaseSearcher(ABC):

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        ...

    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        ...
