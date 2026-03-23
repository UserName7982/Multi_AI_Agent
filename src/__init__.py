from fastapi import FastAPI
from src.api.routes import api
from fastapi.middleware.cors import CORSMiddleware

version = "0.1.0"

app = FastAPI(version=version,title="AI API", description="AI API for various AI services")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)