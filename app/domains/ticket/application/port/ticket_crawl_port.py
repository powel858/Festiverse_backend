from abc import ABC, abstractmethod

from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class TicketCrawlPort(ABC):

    @abstractmethod
    async def crawl(self, vendor_name: str, url: str, mt20id: str) -> TicketInfo | None:
        ...
