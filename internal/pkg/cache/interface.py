import abc
from typing import Protocol


class Cache(Protocol):
    @abc.abstractmethod
    async def ping(self) -> bool:
        ...

    @abc.abstractmethod
    async def set(self, key: str, value: any, expires: float) -> bool:
        ...

    @abc.abstractmethod
    async def get(self, key: str) -> any:
        ...

    @abc.abstractmethod
    async def flash_all(self) -> bool:
        ...

    @abc.abstractmethod
    async def remove_key(self, key: str) -> bool:
        ...
