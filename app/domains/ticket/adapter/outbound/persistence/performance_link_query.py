import json
import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.performance.infrastructure.orm.performance_model import PerformanceModel
from app.domains.ticket.application.port.performance_link_query_port import PerformanceLinkQueryPort

logger = logging.getLogger(__name__)


class PerformanceLinkQuery(PerformanceLinkQueryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_all_booking_links(self) -> list[dict]:
        stmt = select(
            PerformanceModel.mt20id,
            PerformanceModel.relates_json,
        ).where(PerformanceModel.relates_json != "[]")

        result = await self._session.execute(stmt)
        rows = result.all()

        links: list[dict] = []
        for row in rows:
            mt20id = row[0]
            relates_raw = row[1]
            try:
                relates = json.loads(relates_raw) if relates_raw else []
            except (json.JSONDecodeError, TypeError):
                relates = []

            if relates:
                links.append({"mt20id": mt20id, "relates": relates})

        logger.info("예매 링크 조회: %d건", len(links))
        return links

    async def fetch_performances_without_links(self) -> list[dict]:
        stmt = select(
            PerformanceModel.mt20id,
            PerformanceModel.prfnm,
        ).where(
            or_(
                PerformanceModel.relates_json == "[]",
                PerformanceModel.relates_json == "",
                PerformanceModel.relates_json.is_(None),
            )
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        performances = [
            {"mt20id": row[0], "prfnm": row[1] or ""}
            for row in rows
            if row[1]  # 공연명이 있는 경우만
        ]

        logger.info("예매 링크 없는 공연 조회: %d건", len(performances))
        return performances
