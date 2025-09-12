from domain.contracts.repositories import IDomainRepository, IDomainSourceRepository
from domain.entities import AddDomainDto, DomainSourceDto, GetDomainDto


class DomainService:
    def __init__(self, domain_repository: IDomainRepository, source_repository: IDomainSourceRepository):
        self._domain_repository = domain_repository
        self._source_repository = source_repository

    async def create(self, dto: AddDomainDto, source_name: str) -> GetDomainDto | None:
        source = await self._source_repository.get_by_name(source_name)
        if source is None:
            return None

        return await self._domain_repository.create(dto, source.id)

    async def bulk_create(self, dtos: list[AddDomainDto], source_name: str) -> list[GetDomainDto]:
        source = await self._source_repository.get_by_name(source_name)
        if source is None:
            return []

        return await self._domain_repository.bulk_create(dtos, source.id)

    async def get_all(self) -> list[GetDomainDto]:
        return await self._domain_repository.get_all()

    async def get_all_sources(self) -> list[DomainSourceDto]:
        return await self._source_repository.get_all()

    async def get_domain_by_id(self, domain_id: int) -> GetDomainDto | None:
        return await self._domain_repository.get_by_id(domain_id)

    async def get_by_name(self, name: str) -> GetDomainDto | None:
        return await self._domain_repository.get_by_name(name)

    async def remove_by_id(self, domain_id: int) -> GetDomainDto | None:
        return await self._domain_repository.remove_by_id(domain_id)

    async def remove_all(self) -> int:
        return await self._domain_repository.remove_all()
