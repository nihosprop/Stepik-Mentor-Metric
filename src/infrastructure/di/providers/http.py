from collections.abc import AsyncIterable

import aiohttp

from dishka import Provider, Scope, provide


class HttpProvider(Provider):
    @provide(scope=Scope.APP)
    async def client_session(self) -> AsyncIterable[aiohttp.ClientSession]:
        # Connector for Stepik (you can increase the limits)
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=connector) as session:
            yield session
