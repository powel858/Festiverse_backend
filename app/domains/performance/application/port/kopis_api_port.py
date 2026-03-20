from abc import ABC, abstractmethod

from app.domains.performance.domain.entity.performance import Performance
from app.domains.performance.domain.entity.venue import Venue


class KopisApiPort(ABC):

    @abstractmethod
    async def fetch_performance_list(
        self,
        stdate: str,
        eddate: str,
        cpage: int = 1,
        rows: int = 100,
        shcate: str | None = None,
        shprfnm: str | None = None,
        signgucode: str | None = None,
        prfstate: str | None = None,
    ) -> list[Performance]:
        ...

    @abstractmethod
    async def fetch_performance_detail(self, mt20id: str) -> Performance | None:
        ...

    @abstractmethod
    async def fetch_venue_detail(self, mt10id: str) -> Venue | None:
        ...

    @abstractmethod
    async def fetch_festival_list(
        self,
        stdate: str,
        eddate: str,
        cpage: int = 1,
        rows: int = 100,
        shcate: str | None = None,
    ) -> list[Performance]:
        ...
