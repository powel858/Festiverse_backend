from abc import ABC, abstractmethod

from app.domains.performance.domain.entity.performance import Performance


class PerformanceRepositoryPort(ABC):

    @abstractmethod
    async def find_all(
        self,
        stdate: str | None = None,
        eddate: str | None = None,
        genre: str | None = None,
        region: str | None = None,
        keyword: str | None = None,
        state: str | None = None,
        festival: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> list[Performance]:
        ...

    @abstractmethod
    async def find_by_id(self, mt20id: str) -> Performance | None:
        ...

    @abstractmethod
    async def save(self, performance: Performance) -> None:
        ...

    @abstractmethod
    async def save_many(self, performances: list[Performance]) -> None:
        ...
