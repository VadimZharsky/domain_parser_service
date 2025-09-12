from datetime import datetime

from pydantic import BaseModel, Field


class DomainSourceDto(BaseModel):
    id: int
    name: str


class AddDomainDto(BaseModel):
    name: str = Field(validation_alias="fqdn")
    price: int = Field(default=0, validation_alias="current_bid_price")
    bids: int
    domain_created_at: datetime | None = Field(default=None, validation_alias="domain_create_date")
    auction_ended_at: datetime = Field(validation_alias="end_time")


class GetDomainDto(BaseModel):
    id: int
    name: str
    price: int
    bids: int
    collected_at: datetime
    domain_created_at: datetime | None
    auction_ended_at: datetime


class DomainSourceDtoWithDomains(DomainSourceDto):
    domains: list[GetDomainDto]


class DomainDtoWithParent(GetDomainDto):
    source: DomainSourceDto
