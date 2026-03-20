from typing import Optional

from sqlalchemy import Column, DateTime, String, Text

from app.infrastructure.database.base import Base


class PerformanceModel(Base):
    __tablename__ = "performances"

    mt20id = Column(String(50), primary_key=True)
    prfnm = Column(String(500), default="")
    prfpdfrom = Column(String(20), default="")
    prfpdto = Column(String(20), default="")
    fcltynm = Column(String(300), default="")
    prfcast = Column(Text, default="")
    prfcrew = Column(Text, default="")
    prfruntime = Column(String(100), default="")
    prfage = Column(String(100), default="")
    pcseguidance = Column(Text, default="")
    poster = Column(String(1000), default="")
    genrenm = Column(String(100), default="")
    prfstate = Column(String(20), default="")
    openrun = Column(String(10), default="")
    styurls_json = Column(Text, default="[]")
    relates_json = Column(Text, default="[]")
    dtguidance = Column(Text, default="")
    area = Column(String(100), default="")
    mt10id = Column(String(50), default="")
    festival = Column(String(10), default="")
    sty = Column(Text, default="")
    updated_at = Column(DateTime(timezone=True), nullable=True)
