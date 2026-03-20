from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from app.infrastructure.database.base import Base


class TicketInfoModel(Base):
    __tablename__ = "ticket_infos"
    __table_args__ = (
        UniqueConstraint("mt20id", "vendor_name", name="uq_ticket_mt20id_vendor"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    mt20id = Column(String(50), index=True, nullable=False)
    vendor_name = Column(String(100), nullable=False)
    vendor_url = Column(String(1000), default="")
    lineup_json = Column(Text, default="[]")
    prices_json = Column(Text, default="[]")
    booking_status = Column(String(20), default="unknown")
    ticket_open_at = Column(String(100), default="")
    notices_json = Column(Text, default="[]")
    crawled_at = Column(DateTime, nullable=True)
