from sqlalchemy import select
from sqlalchemy.exc import InterfaceError

from domain.contracts.repositories import IDomainSourceRepository
from domain.entities import DomainSourceDto
from infrastructure.database import DbContext, DomainSource
from infrastructure.tools.mappers import DomainSourceMapper


class DomainSourceRepository(IDomainSourceRepository):
    def __init__(self, context: DbContext) -> None:
        self._context = context

    async def get_all(self) -> list[DomainSourceDto]:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(DomainSource))
                sources = res.scalars().all()
                return DomainSourceMapper.to_dto_list(list(sources))
        except (OSError, InterfaceError):
            return []

    async def get_by_name(self, name: str) -> DomainSourceDto | None:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(DomainSource).filter(DomainSource.name == name))
                source = res.scalars().first()
                if not source:
                    return None
                return DomainSourceMapper.to_dto(source)
        except (OSError, InterfaceError):
            return None
