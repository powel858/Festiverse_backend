from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TicketInfo:
    mt20id: str
    vendor_name: str
    vendor_url: str
    lineup: list[str] = field(default_factory=list)
    prices: list[dict[str, str | int | bool]] = field(default_factory=list)
    booking_status: str = "unknown"
    ticket_open_at: str = ""
    notices: list[str] = field(default_factory=list)
    crawled_at: datetime | None = None
