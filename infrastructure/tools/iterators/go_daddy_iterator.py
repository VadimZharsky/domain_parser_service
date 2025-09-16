from typing import Self


class GoDaddyIterator:
    _BASE = "https://auctions.godaddy.com/beta/findApiProxy/v4/aftermarket/find/auction/recommend"
    _END_TIME_AFTER = "endTimeAfter"
    _PAGINATION_SIZE = "paginationSize"
    _PAGINATION_START = "paginationStart"
    _TAIL = "useExtRanker=true&useSemanticSearch=true"

    def __init__(self, size: int) -> None:
        self._collect_max = 0
        self._items_max = 0
        self._start = 0
        self._size = size
        self._time_after: str = ""
        self._filter: str = ""

    @property
    def items_max(self) -> int:
        return self._items_max

    @items_max.setter
    def items_max(self, value: int) -> None:
        self._items_max = value

    @property
    def collect_max(self) -> int:
        return self._collect_max

    @collect_max.setter
    def collect_max(self, value: int) -> None:
        self._collect_max = value

    @property
    def time_after(self) -> str:
        return self._time_after

    @time_after.setter
    def time_after(self, value: str) -> None:
        self._time_after = value

    @property
    def url(self) -> str:
        return self._get_url()

    def set_time_after(self, time_after: str) -> None:
        self._time_after = time_after

    def set_filter(self, this_filter: str) -> None:
        self._filter = this_filter

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        self._start += self._size
        if self._start >= self._items_max:
            raise StopIteration
        if (self._start + self._size) >= self._items_max:
            self._size = self._items_max - self._start

        return self._get_url()

    def _get_url(self) -> str:
        return (
            f"{GoDaddyIterator._BASE}"
            f"?{GoDaddyIterator._END_TIME_AFTER}={self._time_after}&{self._filter}"
            f"&{GoDaddyIterator._PAGINATION_START}={self._start}"
            f"&{GoDaddyIterator._PAGINATION_SIZE}={self._size}"
            f"&{GoDaddyIterator._TAIL}"
        )
