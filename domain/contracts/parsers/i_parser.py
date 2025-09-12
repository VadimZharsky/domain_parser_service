from abc import ABC, abstractmethod


class IParser(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """"""

    @abstractmethod
    async def run(self) -> None:
        """"""
