import http
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from application.constants import AppConstants
from application.providers import DependenciesProvider
from application.routers import DomainRouterSource, domain_router


class App:
    @staticmethod
    def create(provider: DependenciesProvider) -> FastAPI:
        @asynccontextmanager
        async def lifespan(_) -> AsyncGenerator[None, Any]:  # type: ignore
            provider.logger_hub.initialize()
            App._initialize_routers(provider)
            yield

        current_app = FastAPI(
            title=AppConstants.APP_TITLE,
            version=AppConstants.VERSION,
            lifespan=lifespan,
        )

        current_app.include_router(router=domain_router)

        @current_app.middleware("http")
        async def add_process_time_header(request, call_next):  # type: ignore
            start_time = time.time()
            response = await call_next(request)
            url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            host = getattr(getattr(request, "client", None), "host", None)
            port = getattr(getattr(request, "client", None), "port", None)
            try:
                status_phrase = http.HTTPStatus(response.status_code).phrase
            except ValueError:
                status_phrase = ""
            provider.logger_hub.api_log.info(
                f'{host}:{port} - "{request.method} {url}" '
                f"{response.status_code} {status_phrase} {formatted_process_time} ms"
            )
            response.headers["X-Process-Time"] = f"{formatted_process_time} ms"
            return response

        return current_app

    @staticmethod
    def _initialize_routers(provider: DependenciesProvider) -> None:
        DomainRouterSource.set(provider=provider)
