from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
import uvicorn
from src.api.routes import api
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.services import Services
from src.DB.postgres import get_pool
from src.config import config
services = Services()


version = "0.1.0"
@asynccontextmanager # type: ignore
async def lifespan(app: FastAPI):
    app.state.pools={}
    print("Connection pool opened")
    app.state.services = services
    app.state.pools[config.DB_URI]=await get_pool(config.DB_URI)
    app.state.pools[config.DB_URI1]=await get_pool(config.DB_URI1)
    app.state.pools[config.URI]=await get_pool(config.URI)
    await services.initialize(app.state.pools)
    yield
    for pool in app.state.pools.values():
        await pool.close()
    print("Agent closed:","Connection closed")

app = FastAPI(version=version,title="AI API", description="AI API for various AI services",lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)