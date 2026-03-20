from abc import ABC, abstractmethod

from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class BaseParser(ABC):

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        ...

    @abstractmethod
    def parse(self, html: str, url: str, mt20id: str) -> TicketInfo | None:
        ...
