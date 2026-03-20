import re
from datetime import datetime

from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.parsers.base_parser import BaseParser
from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class InterparkParser(BaseParser):

    def can_handle(self, url: str) -> bool:
        return "interpark.com" in url

    def parse(self, html: str, url: str, mt20id: str) -> TicketInfo | None:
        soup = BeautifulSoup(html, "html.parser")

        lineup = self._parse_lineup(soup)
        prices = self._parse_prices(soup)
        booking_status = self._parse_status(soup)
        notices = self._parse_notices(soup)

        return TicketInfo(
            mt20id=mt20id,
            vendor_name="인터파크",
            vendor_url=url,
            lineup=lineup,
            prices=prices,
            booking_status=booking_status,
            ticket_open_at="",
            notices=notices,
            crawled_at=datetime.utcnow(),
        )

    def _parse_lineup(self, soup: BeautifulSoup) -> list[str]:
        lineup: list[str] = []
        for el in soup.select(".castingList li, .casting_info a"):
            name = el.get_text(strip=True)
            if name and name not in lineup:
                lineup.append(name)
        return lineup

    def _parse_prices(self, soup: BeautifulSoup) -> list[dict[str, str | int | bool]]:
        prices: list[dict[str, str | int | bool]] = []
        for el in soup.select(".seatPriceItem, .price_table tr"):
            text = el.get_text(" ", strip=True)
            match = re.search(r"([가-힣A-Za-z\s]+?)\s*[:：]?\s*([\d,]+)\s*원", text)
            if match:
                prices.append({
                    "seat_type": match.group(1).strip(),
                    "price": int(match.group(2).replace(",", "")),
                    "discounted": "할인" in text,
                })
        return prices

    def _parse_status(self, soup: BeautifulSoup) -> str:
        text = soup.get_text()
        if "매진" in text or "sold out" in text.lower():
            return "sold_out"
        if "예매하기" in text:
            return "available"
        return "unknown"

    def _parse_notices(self, soup: BeautifulSoup) -> list[str]:
        notices: list[str] = []
        for el in soup.select(".notice_info li, .noticeList li"):
            text = el.get_text(strip=True)
            if text:
                notices.append(text)
        return notices
