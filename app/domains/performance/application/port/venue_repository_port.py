from abc import ABC, abstractmethod

from app.domains.performance.domain.entity.venue import Venue


class VenueRepositoryPort(ABC):

    @abstractmethod
    async def find_by_id(self, mt10id: str) -> Venue | None:
        ...

    @abstractmethod
    async def save(self, venue: Venue) -> None:
        ...
