import asyncio
import json
import random
from asyncio import Queue as AsyncQueue
from datetime import datetime, timedelta, timezone
from typing import Any

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from domain.contracts.parsers import IParser
from domain.entities.domains import AddDomainDto
from domain.enums import DomainSourceType, FilterType
from infrastructure.tools.iterators import GoDaddyIterator


class GoDaddyPlaywrightParser(IParser):
    _SOURCE_NAME = DomainSourceType.AUCTIONS_GO_DADDY.value
    _INIT_URL = "https://auctions.godaddy.com/beta/"
    _WIDTH = 1368
    _HEIGHT = 768
    _USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36Browser"
    )

    def __init__(
        self,
        collect_size: int,
        pagination_size: int,
        task_pool_max: int,
        filter_type: FilterType,
        queue: AsyncQueue,
    ) -> None:
        self._collect_size = collect_size
        self._pagination_size = pagination_size
        self._task_pool_max = task_pool_max
        self._filter_type = filter_type
        self._queue = queue
        self._playwright: Playwright | None = None
        self._collected = 0
        self._names: list[str] = []

    @property
    def source_name(self) -> str:
        return GoDaddyPlaywrightParser._SOURCE_NAME

    async def run(self) -> None:
        async with async_playwright() as self._playwright:
            await self._proceed_with_browser()

    async def _proceed_with_browser(self) -> None:
        if not self._playwright:
            return

        browser = await GoDaddyPlaywrightParser._create_browser(p=self._playwright)
        context = await GoDaddyPlaywrightParser._create_context(browser=browser)
        page = await context.new_page()
        await page.goto(GoDaddyPlaywrightParser._INIT_URL)
        await page.wait_for_selector(selector="table tbody tr")
        await GoDaddyPlaywrightParser._interact_human_like(page)

        match self._filter_type:
            case FilterType.TIME:
                await self._use_time_filter(context=context)

        await context.close()
        await browser.close()

    async def _use_time_filter(self, context: BrowserContext) -> None:
        semaphore = asyncio.Semaphore(value=self._task_pool_max)
        shift_time = datetime.now(tz=timezone.utc)
        while self._collected < self._collect_size:
            try:
                init_time = shift_time
                shift_time = GoDaddyPlaywrightParser._time_shift(init_time, hours=3)
                iterator = GoDaddyIterator(size=self._pagination_size)
                iterator.time_after = GoDaddyPlaywrightParser._time_repr(init_time)
                iterator.set_filter(
                    this_filter=f"endTimeBefore={GoDaddyPlaywrightParser._time_repr(shift_time)}"
                )
                tasks: list[asyncio.Task] = []
                content = await GoDaddyPlaywrightParser._extract_page_content(
                    context=context,
                    url=iterator.url,
                )
                total_items = GoDaddyPlaywrightParser._get_total_tems(
                    pagination=content.get("pagination", {})
                )
                if total_items == 0:
                    continue

                items: list[dict] = content.get("results", [])
                domains = GoDaddyPlaywrightParser._parse_result_dict(items)
                if len(domains) == 0:
                    continue
                await self._handle_items(domains)
                to_collect = self._collect_size - self._collected
                iterator.items_max = to_collect if to_collect < total_items else total_items
                for step in iterator:
                    tasks.append(
                        asyncio.create_task(
                            coro=self._extract_with_provided_url(
                                context=context,
                                url=step,
                                semaphore=semaphore,
                            )
                        )
                    )
                await asyncio.gather(*tasks)
            except Exception:
                return

    async def _extract_with_provided_url(
        self, context: BrowserContext, url: str, semaphore: asyncio.Semaphore
    ) -> None:
        async with semaphore:
            content = await GoDaddyPlaywrightParser._extract_page_content(context=context, url=url)
            if len(content) == 0:
                return
            items: list[dict] = content.get("results", [])
            domains = GoDaddyPlaywrightParser._parse_result_dict(items)
            await self._handle_items(domains)

    async def _handle_items(self, domains: list[AddDomainDto]) -> None:
        domains_to_add: list[AddDomainDto] = []
        for domain in domains:
            if domain.name not in self._names:
                self._names.append(domain.name)
                domains_to_add.append(domain)
        this_length = len(domains_to_add)
        if this_length > 0:
            self._collected += this_length
            await self._queue.put(domains_to_add)

    @staticmethod
    async def _extract_page_content(context: BrowserContext, url: str) -> dict[str, Any]:
        result = {}
        page = await context.new_page()
        try:
            print(f"load url: {url}")
            await page.goto(url)
            await page.wait_for_selector(selector="body pre")
            await GoDaddyPlaywrightParser._interact_human_like(page)
            result = json.loads(await page.inner_text(selector="body pre"))
        except Exception as e:
            print(e)
        await page.close()
        return result

    @staticmethod
    def _parse_result_dict(items: list[dict[str, Any]]) -> list[AddDomainDto]:
        if len(items) == 0:
            return []
        domains: list[AddDomainDto] = []
        for item in items:
            try:
                domains.append(AddDomainDto(**item))
            except Exception as e:  # noqa
                continue

        return domains

    @staticmethod
    def _get_total_tems(pagination: dict[str, Any]) -> int:
        if len(pagination) == 0:
            return 0
        return int(pagination.get("total", 0))

    @staticmethod
    async def _create_browser(p: Playwright) -> Browser:
        return await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-default-browser-check",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-web-resource",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-dev-shm-usage",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-breakpad",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-ipc-flooding-protection",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--enable-automation",
                "--password-store=basic",
                "--use-mock-keychain",
            ],
        )

    @staticmethod
    async def _create_context(browser: Browser) -> BrowserContext:
        return await browser.new_context(
            viewport={"width": GoDaddyPlaywrightParser._WIDTH, "height": GoDaddyPlaywrightParser._HEIGHT},
            user_agent=GoDaddyPlaywrightParser._USER_AGENT,
            locale="en-US",
            java_script_enabled=True,
            bypass_csp=True,
        )

    @staticmethod
    async def _interact_human_like(page: Page) -> None:
        await page.mouse.move(random.randint(100, 500), random.randint(100, 300), steps=random.randint(5, 20))
        scroll_amount = random.randint(200, 800)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.2, 1.0))

    @staticmethod
    def _time_repr(date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def _time_shift(date: datetime, hours: int) -> datetime:
        return date + timedelta(hours=hours)
