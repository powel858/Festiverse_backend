from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.blog.application.port.performance_title_query_port import PerformanceTitleQueryPort
from app.domains.performance.infrastructure.orm.performance_model import PerformanceModel


class PerformanceTitleQuery(PerformanceTitleQueryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_title(self, mt20id: str) -> str | None:
        stmt = select(PerformanceModel.prfnm).where(PerformanceModel.mt20id == mt20id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row
