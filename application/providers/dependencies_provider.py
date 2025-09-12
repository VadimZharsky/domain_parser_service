from asyncio import Queue as AsyncQueue
from functools import cached_property

from application.factories import ParserFactory
from application.loggers import LoggerHub
from application.managers import ParsingManager
from application.services import DomainService
from application.settings import Settings
from domain.contracts.repositories import IDomainRepository, IDomainSourceRepository
from domain.enums import DomainSourceType
from infrastructure.database import DbContext
from infrastructure.repositories import DomainRepository, DomainSourceRepository


class DependenciesProvider:
    @cached_property
    def config(self) -> Settings:
        return Settings()

    @cached_property
    def logger_hub(self) -> LoggerHub:
        return LoggerHub()

    @cached_property
    def db_context(self) -> DbContext:
        return DbContext(
            url=self.config.db.URL,
        )

    @property
    def domains_repository(self) -> IDomainRepository:
        return DomainRepository(
            context=self.db_context,
        )

    @property
    def source_repository(self) -> IDomainSourceRepository:
        return DomainSourceRepository(
            context=self.db_context,
        )

    @property
    def domains_service(self) -> DomainService:
        return DomainService(
            domain_repository=self.domains_repository,
            source_repository=self.source_repository,
        )

    @property
    def async_queue(self) -> AsyncQueue:
        return AsyncQueue(maxsize=1000)

    def parsing_manager(
        self, collect_size: int, pagination_size: int, source_type: DomainSourceType
    ) -> ParsingManager:
        queue = self.async_queue
        return ParsingManager(
            domains_service=self.domains_service,
            parser=ParserFactory.get(
                collect_size=collect_size,
                pagination_size=pagination_size,
                task_pool_max=self.config.scraper.TASK_POOL_MAX,
                queue=queue,
                source_type=source_type,
            ),
            queue=queue,
        )
