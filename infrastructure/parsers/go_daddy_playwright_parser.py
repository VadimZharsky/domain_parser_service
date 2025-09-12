import asyncio
import json
import random
from asyncio import Queue as AsyncQueue
from datetime import datetime, timezone

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from domain.contracts.parsers import IParser
from domain.entities.domains import AddDomainDto
from domain.enums import DomainSourceType


class GoDaddyPlaywrightParser(IParser):
    _SOURCE_NAME = DomainSourceType.AUCTIONS_GO_DADDY.value
    _INIT_URL = "https://auctions.godaddy.com/beta/"
    _WIDTH = 1024
    _HEIGHT = 768
    _USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36Browser"
    )

    def __init__(
        self, collect_size: int, pagination_size: int, task_pool_max: int, queue: AsyncQueue
    ) -> None:
        self._collect_size = collect_size
        self._pagination_size = pagination_size
        self._task_pool_max = task_pool_max
        self._queue = queue
        self._playwright: Playwright | None = None
        self._utc_now = datetime.now(tz=timezone.utc)
        self._utc_repr = self._utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self._start_pos = 0
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
        tasks: list[asyncio.Task] = []
        semaphore = asyncio.Semaphore(value=self._task_pool_max)
        while self._start_pos < self._collect_size:
            if (self._start_pos + self._pagination_size) <= self._collect_size:
                this_size = self._pagination_size
            else:
                this_size = self._collect_size - self._start_pos

            tasks.append(
                asyncio.create_task(
                    coro=self._extract(
                        context=context,
                        start_pos=self._start_pos,
                        pagination_size=this_size,
                        semaphore=semaphore,
                    )
                )
            )
            self._start_pos += self._pagination_size

        await asyncio.gather(*tasks)
        await context.close()
        await browser.close()

    async def _extract(
        self, context: BrowserContext, start_pos: int, pagination_size: int, semaphore: asyncio.Semaphore
    ) -> None:
        async with semaphore:
            page = await context.new_page()
            try:
                url = (
                    f"{GoDaddyPlaywrightParser._INIT_URL}findApiProxy/v4/aftermarket/find/"
                    f"auction/recommend?endTimeAfter={self._utc_repr}&experimentInfo=auction_eranker_2025%3AB"
                    f"&paginationSize={pagination_size}&paginationStart={start_pos}&sortBy=auctionBids%3Adesc&"
                    f"typeIncludeList=14%2C16%2C38&useExtRanker=true&useSemanticSearch=true"
                )
                await page.goto(url)
                await page.wait_for_selector(selector="body pre")
                html = await page.inner_text(selector="body pre")
                ite = json.loads(html)
                results: list[dict] = ite["results"]
                domains = [AddDomainDto(**r) for r in results]
                names = [entity.name for entity in domains]
                print(url)
                print(f"count: {len(names)}\nnames: {names}")
                domains_to_add: list[AddDomainDto] = []
                for domain in domains:
                    if domain.name not in self._names:
                        domains_to_add.append(domain)
                if len(domains_to_add) > 0:
                    await self._queue.put(domains_to_add)
            except Exception as e:
                print(e)
            await page.close()

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
        await asyncio.sleep(random.uniform(0.5, 2.0))
