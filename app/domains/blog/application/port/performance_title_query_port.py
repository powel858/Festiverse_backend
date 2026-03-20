from abc import ABC, abstractmethod


class PerformanceTitleQueryPort(ABC):

    @abstractmethod
    async def get_title(self, mt20id: str) -> str | None:
        ...
