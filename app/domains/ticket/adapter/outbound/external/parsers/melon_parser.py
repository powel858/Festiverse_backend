import re
from datetime import datetime

from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.parsers.base_parser import BaseParser
from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class MelonParser(BaseParser):

    def can_handle(self, url: str) -> bool:
        return "ticket.melon.com" in url or "melon.com" in url

    def parse(self, html: str, url: str, mt20id: str) -> TicketInfo | None:
        soup = BeautifulSoup(html, "html.parser")

        lineup = self._parse_lineup(soup)
        prices = self._parse_prices(soup)
        ticket_open_at = self._parse_open_date(soup)
        notices = self._parse_notices(soup)
        booking_status = self._parse_status(soup)

        return TicketInfo(
            mt20id=mt20id,
            vendor_name="멜론티켓",
            vendor_url=url,
            lineup=lineup,
            prices=prices,
            booking_status=booking_status,
            ticket_open_at=ticket_open_at,
            notices=notices,
            crawled_at=datetime.utcnow(),
        )

    def _parse_lineup(self, soup: BeautifulSoup) -> list[str]:
        lineup: list[str] = []
        for a_tag in soup.select('li a[href*="/artist/index.htm"]'):
            name = a_tag.get_text(strip=True)
            if name and name not in lineup:
                lineup.append(name)
        return lineup

    def _parse_prices(self, soup: BeautifulSoup) -> list[dict[str, str | int | bool]]:
        prices: list[dict[str, str | int | bool]] = []

        # 멜론티켓 가격 구조: .box_bace_price .list_seat li > .seat_name + .price
        for li in soup.select(".box_bace_price .list_seat li"):
            seat_el = li.select_one(".seat_name")
            price_el = li.select_one(".price")
            if seat_el and price_el:
                seat_type = seat_el.get_text(strip=True)
                match = re.search(r"([\d,]+)", price_el.get_text(strip=True))
                if match:
                    prices.append({
                        "seat_type": seat_type,
                        "price": int(match.group(1).replace(",", "")),
                        "discounted": False,
                    })

        # 할인가 영역이 별도로 있는 경우
        for li in soup.select(".box_dc_price .list_seat li"):
            seat_el = li.select_one(".seat_name")
            price_el = li.select_one(".price")
            if seat_el and price_el:
                seat_type = seat_el.get_text(strip=True)
                match = re.search(r"([\d,]+)", price_el.get_text(strip=True))
                if match:
                    prices.append({
                        "seat_type": seat_type,
                        "price": int(match.group(1).replace(",", "")),
                        "discounted": True,
                    })

        return prices

    def _parse_open_date(self, soup: BeautifulSoup) -> str:
        day_el = soup.select_one(".dateWord.perfDay")
        time_el = soup.select_one(".timeFormat.perfTime")
        parts = []
        if day_el:
            parts.append(day_el.get_text(strip=True))
        if time_el:
            parts.append(time_el.get_text(strip=True))
        return " ".join(parts)

    def _parse_notices(self, soup: BeautifulSoup) -> list[str]:
        notices: list[str] = []
        for box in soup.select(".box_ticketing_type .box_txt"):
            text = box.get_text(strip=True)
            if text:
                notices.append(text)
        return notices

    def _parse_status(self, soup: BeautifulSoup) -> str:
        if soup.select_one(".sold_out"):
            return "sold_out"
        if soup.select_one(".btn_booking") or soup.select_one(".btn_reserve"):
            return "available"
        return "unknown"
