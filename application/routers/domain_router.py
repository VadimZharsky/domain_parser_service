from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.params import Query

from application.builders import JsonResponseBuilder
from application.providers import DependenciesProvider
from domain.entities import DomainSourceDto
from domain.enums import DomainSourceType, FilterType

domain_router = APIRouter(prefix="/api/domains", tags=["Domains"])


class DomainRouterSource:
    _provider: DependenciesProvider | None = None

    @staticmethod
    def set(provider: DependenciesProvider) -> None:
        DomainRouterSource._provider = provider

    @staticmethod
    def get() -> DependenciesProvider:
        if not DomainRouterSource._provider:
            raise RuntimeError()
        return DomainRouterSource._provider


@domain_router.get(
    path="/all_names",
    status_code=status.HTTP_200_OK,
    response_model=list[str],
)
async def get_all_names(provider: DependenciesProvider = Depends(DomainRouterSource.get)) -> Response:
    res = await provider.domains_service.get_all_names()
    return (
        JsonResponseBuilder()
        .with_dict(
            json_dict={
                "count": len(res),
            }
        )
        .with_status(status.HTTP_200_OK)
        .respond()
    )


@domain_router.get(
    path="/sources/all",
    status_code=status.HTTP_200_OK,
    response_model=list[DomainSourceDto],
)
async def get_all_sources(
    provider: DependenciesProvider = Depends(DomainRouterSource.get),
) -> list[DomainSourceDto]:
    return await provider.domains_service.get_all_sources()


@domain_router.get(
    path="/fetch_from",
    status_code=status.HTTP_201_CREATED,
)
async def fetch_from(
    source: Annotated[DomainSourceType, Query()] = DomainSourceType.AUCTIONS_GO_DADDY,
    filter_type: Annotated[FilterType, Query()] = FilterType.TIME,
    size: Annotated[int, Query()] = 100,
    provider: DependenciesProvider = Depends(DomainRouterSource.get),
) -> Response:
    manager = provider.parsing_manager(
        collect_size=size,
        pagination_size=100,
        filter_type=filter_type,
        source_type=source,
    )
    await manager.start()
    return (
        JsonResponseBuilder()
        .with_dict(json_dict={"status": "ok"})
        .with_status(status.HTTP_201_CREATED)
        .respond()
    )


@domain_router.delete(
    path="/clear_domains",
    status_code=status.HTTP_200_OK,
)
async def clear_domains(provider: DependenciesProvider = Depends(DomainRouterSource.get)) -> Response:
    count = await provider.domains_service.remove_all()
    return (
        JsonResponseBuilder()
        .with_dict(json_dict={"status": "ok", "removed": count})
        .with_status(status.HTTP_201_CREATED)
        .respond()
    )
