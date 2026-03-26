import json
from typing import AsyncGenerator, List
from fastapi import File, Request, UploadFile,APIRouter,HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from src.dataIngestionPipelines.VectorIngestion import add_to_db
from ..api.schema import ChatRequest,ChatResponse
from langchain_core.tools import tool

api=APIRouter(prefix="/app",tags=["Files"])

@api.post("/upload")
async def upload_file(request: Request,files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail={"message": "No file to upload"})

    path=await request.app.state.services.upload_file(files)
    if not path:
        raise HTTPException(status_code=400, detail={"message": "No file to upload"})
    try:
        add_to_db(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "File upload failed", "error": str(e)})   
    return JSONResponse({"message": "File uploaded successfully", "files": path})


import json
import logging
import traceback
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

@api.post("/chat", response_model=ChatResponse)
async def User_query(request: Request,query_data: ChatRequest):
    if query_data is None:
        raise HTTPException(status_code=400, detail={"message": "No query to process"})
    
    async def generator() -> AsyncGenerator[str, None]:
        try:
            async for result in request.app.state.services.Answer(query_data):
                if isinstance(result, str):
                    yield result
                elif isinstance(result, list):
                    yield "".join(
                        item if isinstance(item, str) else json.dumps(item)
                        for item in result
                    )
                elif isinstance(result, dict):
                    yield json.dumps(result)
                else:
                    yield str(result)
        except Exception as e:
            # Log the full traceback to see real error
            logger.error(f"Error in generator: {traceback.format_exc()}")
            yield f"Error: {str(e)}"

    try:
        return StreamingResponse(content=generator(), media_type="text/plain")
    except Exception as e:
        logger.error(f"Error in endpoint: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={
            "message": "Error in processing query",
            "error": str(e),
            "traceback": traceback.format_exc()  # 👈 see full error
        })