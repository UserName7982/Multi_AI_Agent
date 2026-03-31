from fastapi import Request
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import  dict_row

async def get_pool(uri:str,MiN_SIZE:int=2,MAX_SIZE:int=10)->AsyncConnectionPool:
    pool=AsyncConnectionPool(
    conninfo=uri,
    kwargs={"autocommit": True, "row_factory": dict_row},
    min_size=MiN_SIZE,
    max_size=MAX_SIZE,
    timeout=60,
    open=False
    )
    await pool.open()
    return pool # type: ignore

async def get_conn(request: Request):
    return request.app.state.pools