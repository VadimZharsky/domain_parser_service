from abc import ABC, abstractmethod

from domain.entities import DomainSourceDto


class IDomainSourceRepository(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> DomainSourceDto | None:
        """"""

    @abstractmethod
    async def get_all(self) -> list[DomainSourceDto]:
        """"""
