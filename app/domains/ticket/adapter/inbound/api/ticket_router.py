from fastapi import APIRouter, Depends

from app.domains.ticket.adapter.outbound.persistence.ticket_repository import TicketRepository
from app.domains.ticket.application.response.ticket_info_response import TicketInfoResponse
from app.domains.ticket.application.usecase.get_ticket_info_usecase import GetTicketInfoUseCase
from app.infrastructure.database.session import async_session_factory

router = APIRouter(prefix="/api", tags=["tickets"])


async def _get_ticket_usecase():
    async with async_session_factory() as session:
        yield GetTicketInfoUseCase(TicketRepository(session))


@router.get("/tickets/{mt20id}", response_model=list[TicketInfoResponse])
async def get_ticket_info(
    mt20id: str,
    usecase: GetTicketInfoUseCase = Depends(_get_ticket_usecase),
) -> list[TicketInfoResponse]:
    return await usecase.execute(mt20id)
