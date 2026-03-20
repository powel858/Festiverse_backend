from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.performance.application.port.venue_repository_port import VenueRepositoryPort
from app.domains.performance.domain.entity.venue import Venue
from app.domains.performance.infrastructure.mapper.venue_mapper import VenueMapper
from app.domains.performance.infrastructure.orm.venue_model import VenueModel


class VenueRepository(VenueRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, mt10id: str) -> Venue | None:
        model = await self._session.get(VenueModel, mt10id)
        if model is None:
            return None
        return VenueMapper.to_entity(model)

    async def save(self, venue: Venue) -> None:
        model = VenueMapper.to_model(venue)
        await self._session.merge(model)
        await self._session.commit()
