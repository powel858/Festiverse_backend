from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ticket.application.port.ticket_repository_port import TicketRepositoryPort
from app.domains.ticket.domain.entity.ticket_info import TicketInfo
from app.domains.ticket.infrastructure.mapper.ticket_info_mapper import TicketInfoMapper
from app.domains.ticket.infrastructure.orm.ticket_info_model import TicketInfoModel


class TicketRepository(TicketRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_mt20id(self, mt20id: str) -> list[TicketInfo]:
        stmt = select(TicketInfoModel).where(TicketInfoModel.mt20id == mt20id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [TicketInfoMapper.to_entity(m) for m in models]

    async def save(self, ticket_info: TicketInfo) -> None:
        # mt20id + vendor_name 기준 upsert
        stmt = select(TicketInfoModel).where(
            TicketInfoModel.mt20id == ticket_info.mt20id,
            TicketInfoModel.vendor_name == ticket_info.vendor_name,
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        new_model = TicketInfoMapper.to_model(ticket_info)

        if existing is not None:
            existing.vendor_url = new_model.vendor_url
            existing.lineup_json = new_model.lineup_json
            existing.prices_json = new_model.prices_json
            existing.booking_status = new_model.booking_status
            existing.ticket_open_at = new_model.ticket_open_at
            existing.notices_json = new_model.notices_json
            existing.crawled_at = new_model.crawled_at
        else:
            self._session.add(new_model)

        await self._session.commit()

    async def save_many(self, ticket_infos: list[TicketInfo]) -> None:
        for t in ticket_infos:
            await self.save(t)
