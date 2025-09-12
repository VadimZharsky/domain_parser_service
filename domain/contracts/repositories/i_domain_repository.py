from abc import ABC, abstractmethod

from domain.entities import AddDomainDto, GetDomainDto


class IDomainRepository(ABC):
    @abstractmethod
    async def create(self, dto: AddDomainDto, source_id: int) -> GetDomainDto | None:
        """"""

    @abstractmethod
    async def bulk_create(self, dtos: list[AddDomainDto], source_id: int) -> list[GetDomainDto]:
        """"""

    @abstractmethod
    async def get_all(self) -> list[GetDomainDto]:
        """"""

    @abstractmethod
    async def get_by_id(self, domain_id: int) -> GetDomainDto | None:
        """"""

    @abstractmethod
    async def get_by_name(self, name: str) -> GetDomainDto | None:
        """"""

    @abstractmethod
    async def remove_by_id(self, domain_id: int) -> GetDomainDto | None:
        """"""

    @abstractmethod
    async def remove_all(self) -> int:
        """"""
