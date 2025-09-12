import asyncio
from asyncio import Queue as AsyncQueue

from application.services.domain_service import DomainService
from domain.contracts.parsers import IParser
from domain.entities import AddDomainDto


class ParsingManager:
    def __init__(self, domains_service: DomainService, parser: IParser, queue: AsyncQueue) -> None:
        self._domains_service = domains_service
        self._parser = parser
        self._queue = queue
        self._is_active = True
        self._main_task: asyncio.Task | None = None
        self._tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        self._main_task = asyncio.create_task(self._start_tasks())

    async def _start_tasks(self) -> None:
        self._tasks.append(asyncio.create_task(coro=self._parser.run()))
        self._tasks.append(asyncio.create_task(coro=self._consume()))

        while True:
            if self._is_active is False:
                await self._stop()
                break
            else:
                await asyncio.sleep(1)

        print("main task finished")

    async def _stop(self) -> None:
        [t.cancel() for t in self._tasks]
        print("all subtasks finished")

    async def _consume(self) -> None:
        while self._is_active:
            dtos: list[AddDomainDto] = await self._read_queue()
            if self._is_active is False:
                return
            await self._domains_service.bulk_create(dtos=dtos, source_name=self._parser.source_name)

    async def _read_queue(self) -> list[AddDomainDto]:
        data: list[AddDomainDto] = []
        try:
            data = await asyncio.wait_for(self._queue.get(), timeout=20)
        except asyncio.TimeoutError:
            self._is_active = False
        return data
