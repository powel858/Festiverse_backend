import json
import re
import unicodedata
from datetime import datetime

from bs4 import BeautifulSoup

from app.domains.ticket.adapter.outbound.external.parsers.base_parser import BaseParser
from app.domains.ticket.domain.entity.ticket_info import TicketInfo


class TicketlinkParser(BaseParser):

    def can_handle(self, url: str) -> bool:
        return "ticketlink.co.kr" in url

    def parse(self, html: str, url: str, mt20id: str) -> TicketInfo | None:
        soup = BeautifulSoup(html, "html.parser")

        lineup: list[str] = []
        jsonld_prices: list[dict[str, str | int | bool]] = []
        booking_status = "unknown"
        ticket_open_at = ""
        notices: list[str] = []

        # JSON-LD 파싱
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "")
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            # Schema.org PerformingGroup → 라인업
            performers = data.get("performer") or data.get("performers") or []
            if isinstance(performers, dict):
                performers = [performers]
            for p in performers:
                if isinstance(p, dict):
                    name = p.get("name", "")
                    if name and name not in lineup:
                        lineup.append(name)

            # Event 타입의 JSON-LD만 파싱 (Product 중복 방지)
            schema_type = data.get("@type", "")
            if schema_type != "Event":
                continue

            # offers → 가격
            offers = data.get("offers") or []
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                if isinstance(offer, dict):
                    price_val = offer.get("price")
                    # name이 없으면 상위 Event name에서 추출 시도
                    seat_type = offer.get("name") or data.get("name", "일반")
                    if price_val is not None:
                        try:
                            jsonld_prices.append({
                                "seat_type": str(seat_type),
                                "price": int(float(str(price_val))),
                                "discounted": False,
                            })
                        except (ValueError, TypeError):
                            pass

                    # availability → 예매 상태
                    avail = offer.get("availability", "")
                    if "SoldOut" in str(avail):
                        booking_status = "sold_out"
                    elif "InStock" in str(avail):
                        booking_status = "available"

            # startDate → 공연 시작일
            if not ticket_open_at:
                start = data.get("startDate", "")
                if start:
                    ticket_open_at = str(start)

        # HTML 가격 파싱 (항상 실행하여 할인 가격 포함)
        html_prices = self._parse_prices_html(soup)

        # JSON-LD + HTML 가격 병합
        prices = self._merge_prices(jsonld_prices, html_prices)

        # HTML 폴백: 공지사항
        notices = self._parse_notices_html(soup)

        return TicketInfo(
            mt20id=mt20id,
            vendor_name="티켓링크",
            vendor_url=url,
            lineup=lineup,
            prices=prices,
            booking_status=booking_status,
            ticket_open_at=ticket_open_at,
            notices=notices,
            crawled_at=datetime.utcnow(),
        )

    @staticmethod
    def _normalize_seat_type(seat_type: str) -> str:
        """좌석 타입을 정규화하여 비교 가능하게 만든다."""
        text = unicodedata.normalize("NFC", seat_type)
        text = re.sub(r"\s+", "", text)
        return text.upper()

    def _merge_prices(
        self,
        jsonld_prices: list[dict[str, str | int | bool]],
        html_prices: list[dict[str, str | int | bool]],
    ) -> list[dict[str, str | int | bool]]:
        """JSON-LD와 HTML 가격을 병합하고 중복 제거한다.

        - (정규화된 seat_type, price) 기준으로 중복 제거
        - HTML에서만 발견된 더 낮은 가격은 discounted=True로 표시
        """
        if not jsonld_prices and not html_prices:
            return []
        if not jsonld_prices:
            return html_prices
        if not html_prices:
            return jsonld_prices

        merged: list[dict[str, str | int | bool]] = list(jsonld_prices)
        seen: set[tuple[str, int]] = {
            (self._normalize_seat_type(str(p["seat_type"])), int(p["price"]))
            for p in jsonld_prices
        }

        # JSON-LD에 존재하는 좌석 타입별 최저 가격 (할인 판단용)
        jsonld_min_by_type: dict[str, int] = {}
        for p in jsonld_prices:
            norm = self._normalize_seat_type(str(p["seat_type"]))
            price = int(p["price"])
            if norm not in jsonld_min_by_type or price < jsonld_min_by_type[norm]:
                jsonld_min_by_type[norm] = price

        for hp in html_prices:
            key = (self._normalize_seat_type(str(hp["seat_type"])), int(hp["price"]))
            if key in seen:
                continue
            seen.add(key)

            # HTML에서만 발견되었고 같은 좌석 타입의 JSON-LD 가격보다 낮으면 할인
            norm_type = key[0]
            price = key[1]
            is_discounted = hp.get("discounted", False)
            if norm_type in jsonld_min_by_type and price < jsonld_min_by_type[norm_type]:
                is_discounted = True

            merged.append({
                "seat_type": hp["seat_type"],
                "price": hp["price"],
                "discounted": is_discounted,
            })

        return merged

    def _parse_prices_html(self, soup: BeautifulSoup) -> list[dict[str, str | int | bool]]:
        prices: list[dict[str, str | int | bool]] = []
        for el in soup.select(".price_table tr, .price_info li"):
            text = el.get_text(" ", strip=True)
            match = re.search(r"([가-힣A-Za-z\s]+?)\s*[:：]?\s*([\d,]+)\s*원", text)
            if match:
                prices.append({
                    "seat_type": match.group(1).strip(),
                    "price": int(match.group(2).replace(",", "")),
                    "discounted": "할인" in text,
                })
        return prices

    def _parse_notices_html(self, soup: BeautifulSoup) -> list[str]:
        notices: list[str] = []
        for el in soup.select(".notice_info li, .info_notice p"):
            text = el.get_text(strip=True)
            if text:
                notices.append(text)
        return notices
