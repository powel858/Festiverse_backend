from abc import ABC, abstractmethod


class PerformanceLinkQueryPort(ABC):

    @abstractmethod
    async def fetch_all_booking_links(self) -> list[dict]:
        """모든 공연의 예매 링크를 조회한다.

        Returns:
            [{"mt20id": "PF12345", "relates": [{"name": "멜론티켓", "url": "..."}]}]
        """
        ...

    @abstractmethod
    async def fetch_performances_without_links(self) -> list[dict]:
        """예매 링크(relates)가 없는 공연 목록을 조회한다.

        Returns:
            [{"mt20id": "PF12345", "prfnm": "공연명"}]
        """
        ...
