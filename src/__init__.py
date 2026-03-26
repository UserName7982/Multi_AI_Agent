from fastapi import FastAPI
from src.api.routes import api
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.Agentic.Agent import get_graph
from src.api.services import Services

services = Services()


version = "0.1.0"
graph_app=None
@asynccontextmanager # type: ignore
async def lifespan(app: FastAPI):
    global graph_app
    await services.initialize()
    app.state.services = services
    graph_app=await get_graph()
    yield

app = FastAPI(version=version,title="AI API", description="AI API for various AI services",lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)