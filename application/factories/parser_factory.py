from asyncio import Queue as AsyncQueue

from domain.contracts.parsers import IParser
from domain.enums import DomainSourceType, FilterType
from infrastructure.parsers import GoDaddyPlaywrightParser


class ParserFactory:
    @staticmethod
    def get(
        collect_size: int,
        pagination_size: int,
        task_pool_max: int,
        filter_type: FilterType,
        queue: AsyncQueue,
        source_type: DomainSourceType,
    ) -> IParser:
        match source_type:
            case DomainSourceType.AUCTIONS_GO_DADDY:
                return ParserFactory._as_godaddy_parser(
                    collect_size=collect_size,
                    pagination_size=pagination_size,
                    task_pool_max=task_pool_max,
                    filter_type=filter_type,
                    queue=queue,
                )
            case _:
                raise NotImplementedError(f"can not instantiate parser for source type {source_type.value}")

    @staticmethod
    def _as_godaddy_parser(
        collect_size: int,
        pagination_size: int,
        task_pool_max: int,
        filter_type: FilterType,
        queue: AsyncQueue,
    ) -> IParser:
        return GoDaddyPlaywrightParser(
            collect_size=collect_size,
            pagination_size=pagination_size,
            task_pool_max=task_pool_max,
            filter_type=filter_type,
            queue=queue,
        )
