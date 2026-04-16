from collections.abc import AsyncIterable

import aiohttp

from dishka import Provider, Scope, provide


class HttpProvider(Provider):
    @provide(scope=Scope.APP)
    async def client_session(self) -> AsyncIterable[aiohttp.ClientSession]:
        # Connector for Stepik (you can increase the limits)
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=30, sock_connect=10)

        async with aiohttp.ClientSession(connector=connector,
                                         timeout=timeout) as session:
            yield session
