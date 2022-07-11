import json

from internal.pkg.cache.interface import Cache
from redis import asyncio as aioredis


class RedisCache(Cache):
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.redis = aioredis.Redis(host=host, port=port, socket_connect_timeout=5)

    async def ping(self) -> bool:
        return await self.redis.ping()

    async def set(self, key: str, value: any, expires: float) -> bool:
        """ Set cache <key=value>

        :param key: ...
        :param value: ...
        :param expires: key retention time at seconds
        :return: ...
        """
        return await self.redis.set(key, json.dumps(value), ex=expires)

    async def get(self, key: str) -> any:
        if res := await self.redis.get(key):
            return json.loads(res)
        return res

    async def remove_key(self, key: str) -> bool:
        return await self.redis.delete(key)

    async def flash_all(self) -> bool:
        """ Clear all keys in cache storage.

        :rtype: ...
        """
        return await self.redis.flushall()
