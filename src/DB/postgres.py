from psycopg_pool import AsyncConnectionPool, ConnectionPool
from psycopg.rows import dict_row


class PoolManager:
    _async_pools: dict[str, AsyncConnectionPool] = {}
    _sync_pools: dict[str, ConnectionPool] = {}

    @classmethod
    async def get_async_pool(
        cls, uri: str, min_size: int = 2, max_size: int = 10
    ) -> AsyncConnectionPool:
        if uri in cls._async_pools:
            return cls._async_pools[uri]

        pool = AsyncConnectionPool(
            conninfo=uri,
            kwargs={"autocommit": True, "row_factory": dict_row},
            min_size=min_size,
            max_size=max_size,
            timeout=60,
            open=False,
        )
        await pool.open()
        await pool.wait()  
        cls._async_pools[uri] = pool # type: ignore
        return pool # type: ignore

    @classmethod
    def get_sync_pool(
        cls, uri: str, min_size: int = 2, max_size: int = 10
    ) -> ConnectionPool:
        if uri in cls._sync_pools:
            return cls._sync_pools[uri]

        pool = ConnectionPool(
            conninfo=uri,
            kwargs={"autocommit": True, "row_factory": dict_row},
            min_size=min_size,
            max_size=max_size,
            timeout=60,
            open=True,
        )
        pool.wait()  
        cls._sync_pools[uri] = pool # type: ignore
        return pool # type: ignore

    @classmethod
    async def close_async(cls) -> None:
        for pool in cls._async_pools.values():
            await pool.close()
        cls._async_pools.clear()

    @classmethod
    def close_sync(cls) -> None:
        for pool in cls._sync_pools.values():
            pool.close()
        cls._sync_pools.clear()