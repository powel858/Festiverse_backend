from pydantic import BaseModel

from app.domains.performance.application.response.venue_response import VenueResponse


class RelateResponse(BaseModel):
    name: str
    url: str


class DiscountInfoResponse(BaseModel):
    seat_type: str
    price: int
    vendor_name: str


class PerformanceDetailResponse(BaseModel):
    mt20id: str
    prfnm: str
    prfpdfrom: str
    prfpdto: str
    fcltynm: str
    prfcast: str
    prfcrew: str
    prfruntime: str
    prfage: str
    pcseguidance: str
    poster: str
    genrenm: str
    prfstate: str
    openrun: str
    styurls: list[str]
    relates: list[RelateResponse]
    dtguidance: str
    area: str
    sty: str
    venue: VenueResponse | None = None
    discounts: list[DiscountInfoResponse] = []

    model_config = {"from_attributes": True}
