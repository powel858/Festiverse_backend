import json

from app.domains.ticket.domain.entity.ticket_info import TicketInfo
from app.domains.ticket.infrastructure.orm.ticket_info_model import TicketInfoModel


class TicketInfoMapper:

    @staticmethod
    def to_entity(model: TicketInfoModel) -> TicketInfo:
        lineup: list[str] = []
        if model.lineup_json:
            try:
                lineup = json.loads(model.lineup_json)
            except (json.JSONDecodeError, TypeError):
                lineup = []

        prices: list[dict[str, str | int | bool]] = []
        if model.prices_json:
            try:
                prices = json.loads(model.prices_json)
            except (json.JSONDecodeError, TypeError):
                prices = []

        notices: list[str] = []
        if model.notices_json:
            try:
                notices = json.loads(model.notices_json)
            except (json.JSONDecodeError, TypeError):
                notices = []

        return TicketInfo(
            mt20id=model.mt20id,
            vendor_name=model.vendor_name,
            vendor_url=model.vendor_url or "",
            lineup=lineup,
            prices=prices,
            booking_status=model.booking_status or "unknown",
            ticket_open_at=model.ticket_open_at or "",
            notices=notices,
            crawled_at=model.crawled_at,
        )

    @staticmethod
    def to_model(entity: TicketInfo) -> TicketInfoModel:
        return TicketInfoModel(
            mt20id=entity.mt20id,
            vendor_name=entity.vendor_name,
            vendor_url=entity.vendor_url,
            lineup_json=json.dumps(entity.lineup, ensure_ascii=False),
            prices_json=json.dumps(entity.prices, ensure_ascii=False),
            booking_status=entity.booking_status,
            ticket_open_at=entity.ticket_open_at,
            notices_json=json.dumps(entity.notices, ensure_ascii=False),
            crawled_at=entity.crawled_at,
        )
