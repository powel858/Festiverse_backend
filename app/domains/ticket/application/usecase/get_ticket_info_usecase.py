from app.domains.ticket.application.port.ticket_repository_port import TicketRepositoryPort
from app.domains.ticket.application.response.ticket_info_response import (
    TicketInfoResponse,
    TicketPriceResponse,
)


class GetTicketInfoUseCase:

    def __init__(self, ticket_repo: TicketRepositoryPort) -> None:
        self._ticket_repo = ticket_repo

    async def execute(self, mt20id: str) -> list[TicketInfoResponse]:
        tickets = await self._ticket_repo.find_by_mt20id(mt20id)
        return [
            TicketInfoResponse(
                mt20id=t.mt20id,
                vendor_name=t.vendor_name,
                vendor_url=t.vendor_url,
                lineup=t.lineup,
                prices=[
                    TicketPriceResponse(
                        seat_type=p.get("seat_type", ""),
                        price=p.get("price", 0),
                        discounted=p.get("discounted", False),
                    )
                    for p in t.prices
                ],
                booking_status=t.booking_status,
                ticket_open_at=t.ticket_open_at,
                notices=t.notices,
                crawled_at=t.crawled_at,
            )
            for t in tickets
        ]
