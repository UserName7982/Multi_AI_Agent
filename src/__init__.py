import asyncio
from fastapi import FastAPI
from src.api.routes import api
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.services import Services
from src.DB.postgres import PoolManager
from src.config import config
from src.taskscheduling.schedular import schedule_loop


services = Services()

version = "0.1.0"
@asynccontextmanager # type: ignore
async def lifespan(app: FastAPI):
    app.state.pools={}
    print("Connection pool opened")
    app.state.services = services
    app.state.pools[config.DB_URI]=await PoolManager.get_async_pool(config.DB_URI)
    app.state.pools[config.DB_URI1]=await PoolManager.get_async_pool(config.DB_URI1)
    app.state.pools[config.URI]=await PoolManager.get_async_pool(config.URI)
    await services.initialize(app.state.pools)
    scheduler_task = asyncio.create_task(schedule_loop(100, app))
    print("scheduler started")
    yield
    scheduler_task.cancel()
    await PoolManager.close_async()
    PoolManager.close_sync()
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