from pydantic import BaseModel


class VenueResponse(BaseModel):
    mt10id: str
    fcltynm: str
    seatscale: int
    telno: str
    relateurl: str
    adres: str
    la: float
    lo: float
    parkinglot: str
    restaurant: str
    cafe: str
    store: str
    disability: str

    model_config = {"from_attributes": True}
