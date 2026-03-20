from abc import ABC, abstractmethod

from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class TicketRepositoryPort(ABC):

    @abstractmethod
    async def find_by_mt20id(self, mt20id: str) -> list[TicketInfo]:
        ...

    @abstractmethod
    async def save(self, ticket_info: TicketInfo) -> None:
        ...

    @abstractmethod
    async def save_many(self, ticket_infos: list[TicketInfo]) -> None:
        ...
