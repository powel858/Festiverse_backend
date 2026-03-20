import logging
import xml.etree.ElementTree as ET

import httpx

from app.domains.performance.application.port.kopis_api_port import KopisApiPort
from app.domains.performance.domain.entity.performance import Performance
from app.domains.performance.domain.entity.venue import Venue

logger = logging.getLogger(__name__)


def _text(element: ET.Element | None, tag: str, default: str = "") -> str:
    """XML 요소에서 텍스트 추출. 없거나 None이면 기본값 반환."""
    if element is None:
        return default
    child = element.find(tag)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _int(element: ET.Element | None, tag: str, default: int = 0) -> int:
    text = _text(element, tag, "")
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def _float(element: ET.Element | None, tag: str, default: float = 0.0) -> float:
    text = _text(element, tag, "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


class KopisApiAdapter(KopisApiPort):

    def __init__(self, client: httpx.AsyncClient, base_url: str, api_key: str) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def fetch_performance_list(
        self,
        stdate: str,
        eddate: str,
        cpage: int = 1,
        rows: int = 100,
        shcate: str | None = None,
        shprfnm: str | None = None,
        signgucode: str | None = None,
        prfstate: str | None = None,
    ) -> list[Performance]:
        params: dict[str, str | int] = {
            "service": self._api_key,
            "stdate": stdate,
            "eddate": eddate,
            "cpage": cpage,
            "rows": rows,
        }
        if shcate:
            params["shcate"] = shcate
        if shprfnm:
            params["shprfnm"] = shprfnm
        if signgucode:
            params["signgucode"] = signgucode
        if prfstate:
            params["prfstate"] = prfstate

        return await self._fetch_list(f"{self._base_url}/pblprfr", params, is_festival=False)

    async def fetch_performance_detail(self, mt20id: str) -> Performance | None:
        params = {"service": self._api_key}
        try:
            resp = await self._client.get(f"{self._base_url}/pblprfr/{mt20id}", params=params)
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.exception("공연 상세 조회 실패: %s", mt20id)
            return None

        root = ET.fromstring(resp.text)
        db = root.find(".//db")
        if db is None:
            return None

        # styurls 파싱
        styurls: list[str] = []
        styurls_el = db.find("styurls")
        if styurls_el is not None:
            for styurl_el in styurls_el.findall("styurl"):
                if styurl_el.text:
                    styurls.append(styurl_el.text.strip())

        # relates (예매 링크) 파싱
        relates: list[dict[str, str]] = []
        relates_el = db.find("relates")
        if relates_el is not None:
            for relate_el in relates_el.findall("relate"):
                name = _text(relate_el, "relatenm")
                url = _text(relate_el, "relateurl")
                if name or url:
                    relates.append({"name": name, "url": url})

        return Performance(
            mt20id=_text(db, "mt20id"),
            prfnm=_text(db, "prfnm"),
            prfpdfrom=_text(db, "prfpdfrom"),
            prfpdto=_text(db, "prfpdto"),
            fcltynm=_text(db, "fcltynm"),
            prfcast=_text(db, "prfcast"),
            prfcrew=_text(db, "prfcrew"),
            prfruntime=_text(db, "prfruntime"),
            prfage=_text(db, "prfage"),
            pcseguidance=_text(db, "pcseguidance"),
            poster=_text(db, "poster"),
            genrenm=_text(db, "genrenm"),
            prfstate=_text(db, "prfstate"),
            openrun=_text(db, "openrun"),
            styurls=styurls,
            relates=relates,
            dtguidance=_text(db, "dtguidance"),
            area=_text(db, "area"),
            mt10id=_text(db, "mt10id"),
            festival=_text(db, "festival"),
            sty=_text(db, "sty"),
        )

    async def fetch_venue_detail(self, mt10id: str) -> Venue | None:
        params = {"service": self._api_key}
        try:
            resp = await self._client.get(f"{self._base_url}/prfplc/{mt10id}", params=params)
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.exception("공연시설 상세 조회 실패: %s", mt10id)
            return None

        root = ET.fromstring(resp.text)
        db = root.find(".//db")
        if db is None:
            return None

        return Venue(
            mt10id=_text(db, "mt10id"),
            fcltynm=_text(db, "fcltynm"),
            mt13cnt=_int(db, "mt13cnt"),
            fcltychartr=_text(db, "fcltychartr"),
            opende=_text(db, "opende"),
            seatscale=_int(db, "seatscale"),
            telno=_text(db, "telno"),
            relateurl=_text(db, "relateurl"),
            adres=_text(db, "adres"),
            la=_float(db, "la"),
            lo=_float(db, "lo"),
            parkinglot=_text(db, "parkinglot"),
            restaurant=_text(db, "restaurant"),
            cafe=_text(db, "cafe"),
            store=_text(db, "store"),
            nolibang=_text(db, "nolibang"),
            suyu=_text(db, "suyu"),
            disability=_text(db, "disability"),
        )

    async def fetch_festival_list(
        self,
        stdate: str,
        eddate: str,
        cpage: int = 1,
        rows: int = 100,
        shcate: str | None = None,
    ) -> list[Performance]:
        params: dict[str, str | int] = {
            "service": self._api_key,
            "stdate": stdate,
            "eddate": eddate,
            "cpage": cpage,
            "rows": rows,
        }
        if shcate:
            params["shcate"] = shcate

        return await self._fetch_list(f"{self._base_url}/prffest", params, is_festival=True)

    async def _fetch_list(self, url: str, params: dict, is_festival: bool) -> list[Performance]:
        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.exception("목록 조회 실패: %s", url)
            return []

        root = ET.fromstring(resp.text)
        results: list[Performance] = []
        for db in root.findall(".//db"):
            results.append(Performance(
                mt20id=_text(db, "mt20id"),
                prfnm=_text(db, "prfnm"),
                prfpdfrom=_text(db, "prfpdfrom"),
                prfpdto=_text(db, "prfpdto"),
                fcltynm=_text(db, "fcltynm"),
                poster=_text(db, "poster"),
                genrenm=_text(db, "genrenm"),
                prfstate=_text(db, "prfstate"),
                area=_text(db, "area"),
                festival="Y" if is_festival else _text(db, "festival"),
            ))
        return results
