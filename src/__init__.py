from fastapi import FastAPI
from src.api.routes import api

version = "0.1.0"

app = FastAPI(version=version,title="AI API", description="AI API for various AI services")
app.include_router(api)