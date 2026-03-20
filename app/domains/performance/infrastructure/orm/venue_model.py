from sqlalchemy import Column, Float, Integer, String

from app.infrastructure.database.base import Base


class VenueModel(Base):
    __tablename__ = "venues"

    mt10id = Column(String(50), primary_key=True)
    fcltynm = Column(String(300), default="")
    mt13cnt = Column(Integer, default=0)
    fcltychartr = Column(String(200), default="")
    opende = Column(String(20), default="")
    seatscale = Column(Integer, default=0)
    telno = Column(String(100), default="")
    relateurl = Column(String(500), default="")
    adres = Column(String(500), default="")
    la = Column(Float, default=0.0)
    lo = Column(Float, default=0.0)
    parkinglot = Column(String(50), default="")
    restaurant = Column(String(50), default="")
    cafe = Column(String(50), default="")
    store = Column(String(50), default="")
    nolibang = Column(String(50), default="")
    suyu = Column(String(50), default="")
    disability = Column(String(50), default="")
