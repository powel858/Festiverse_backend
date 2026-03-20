from datetime import datetime

from pydantic import BaseModel


class TicketPriceResponse(BaseModel):
    seat_type: str
    price: int
    discounted: bool = False


class TicketInfoResponse(BaseModel):
    mt20id: str
    vendor_name: str
    vendor_url: str
    lineup: list[str]
    prices: list[TicketPriceResponse]
    booking_status: str
    ticket_open_at: str
    notices: list[str]
    crawled_at: datetime | None = None

    model_config = {"from_attributes": True}
