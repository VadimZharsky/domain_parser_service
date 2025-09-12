import sqlalchemy.exc
from sqlalchemy import delete, select

from domain.contracts.repositories import IDomainRepository
from domain.entities import AddDomainDto, GetDomainDto
from infrastructure.database import DbContext, Domain
from infrastructure.tools.mappers import DomainMapper


class DomainRepository(IDomainRepository):
    def __init__(self, context: DbContext):
        self._context = context

    async def create(self, dto: AddDomainDto, source_id: int) -> GetDomainDto | None:
        try:
            domain = DomainMapper.from_dto(dto, source_id)
            async with self._context.session() as session:
                session.add(domain)
                await session.commit()
                await session.refresh(domain)
                return DomainMapper.to_dto(domain)
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return None

    async def bulk_create(self, dtos: list[AddDomainDto], source_id: int) -> list[GetDomainDto]:
        existed_domains = await self.get_all()
        existed_names = [d.name for d in existed_domains]
        dto_to_add: list[AddDomainDto] = []
        for dto in dtos:
            if dto.name in existed_names:
                continue
            dto_to_add.append(dto)
        if len(dto_to_add) == 0:
            return []
        try:
            domains = DomainMapper.from_dto_list(dto_to_add, source_id)
            async with self._context.session() as session:
                session.add_all(domains)
                await session.commit()
                return DomainMapper.to_dto_list(domains)
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return []

    async def get_all(self) -> list[GetDomainDto]:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(Domain))
                domains = res.scalars().all()
                return DomainMapper.to_dto_list(list(domains))
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return []

    async def get_by_id(self, domain_id: int) -> GetDomainDto | None:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(Domain).filter(Domain.id == domain_id))
                domain = res.scalars().first()
                if not domain:
                    return None
                return DomainMapper.to_dto(domain)
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return None

    async def get_by_name(self, name: str) -> GetDomainDto | None:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(Domain).filter(Domain.name == name))
                domain = res.scalars().first()
                if not domain:
                    return None
                return DomainMapper.to_dto(domain)
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return None

    async def remove_by_id(self, domain_id: int) -> GetDomainDto | None:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=select(Domain).filter(Domain.id == domain_id))
                domain = res.scalars().first()
                if not domain:
                    return None
                dto = DomainMapper.to_dto(domain)
                await session.delete(domain)
                await session.commit()
                return dto
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return None

    async def remove_all(self) -> int:
        try:
            async with self._context.session() as session:
                res = await session.execute(statement=delete(Domain))
                count = res.rowcount
                await session.commit()
                return int(count)
        except (OSError, sqlalchemy.exc.InterfaceError, sqlalchemy.exc.IntegrityError):
            return 0
