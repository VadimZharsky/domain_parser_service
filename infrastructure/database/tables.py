from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class DomainParserBase(DeclarativeBase): ...


class DomainSource(DomainParserBase):
    __tablename__ = "domain_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    domains = relationship("Domain", back_populates="source")


class Domain(DomainParserBase):
    __tablename__ = "domains"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    bids: Mapped[int] = mapped_column(Integer, nullable=False)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(tz=timezone.utc), nullable=False
    )
    domain_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    auction_ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    domain_source_id: Mapped[int] = mapped_column(Integer, ForeignKey("domain_sources.id"), nullable=False)

    source = relationship("DomainSource", back_populates="domains")
