from domain.entities import AddDomainDto, DomainSourceDto, DomainSourceDtoWithDomains, GetDomainDto
from infrastructure.database import Domain, DomainSource


class DomainMapper:
    @staticmethod
    def from_dto_list(dtos: list[AddDomainDto], source_id: int) -> list[Domain]:
        return [DomainMapper.from_dto(dto, source_id) for dto in dtos]

    @staticmethod
    def to_dto_list(domains: list[Domain]) -> list[GetDomainDto]:
        return [DomainMapper.to_dto(domain) for domain in domains]

    @staticmethod
    def from_dto(dto: AddDomainDto, source_id: int) -> Domain:
        return Domain(
            name=dto.name,
            price=dto.price,
            bids=dto.bids,
            domain_created_at=dto.domain_created_at,
            auction_ended_at=dto.auction_ended_at,
            domain_source_id=source_id,
        )

    @staticmethod
    def to_dto(domain: Domain) -> GetDomainDto:
        return GetDomainDto(
            id=domain.id,
            name=domain.name,
            price=domain.price,
            bids=domain.bids,
            collected_at=domain.collected_at,
            domain_created_at=domain.domain_created_at,
            auction_ended_at=domain.auction_ended_at,
        )


class DomainSourceMapper:
    @staticmethod
    def to_dto_list(sources: list[DomainSource]) -> list[DomainSourceDto]:
        return [DomainSourceMapper.to_dto(source) for source in sources]

    @staticmethod
    def from_dto(dto: DomainSourceDto) -> DomainSource:
        return DomainSource(
            name=dto.name,
        )

    @staticmethod
    def to_dto(source: DomainSource) -> DomainSourceDto:
        return DomainSourceDto(
            id=source.id,
            name=source.name,
        )

    @staticmethod
    def to_dto_with_domains(source: DomainSource) -> DomainSourceDtoWithDomains:
        return DomainSourceDtoWithDomains(
            id=source.id,
            name=source.name,
            domains=DomainMapper.to_dto_list(source.domains),
        )
