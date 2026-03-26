from typing import List
from fastapi import File, UploadFile,APIRouter,HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.services import Services
from src.dataIngestionPipelines.VectorIngestion import add_to_db
from ..api.schema import ChatRequest,ChatResponse
from langchain_core.tools import tool

api=APIRouter(prefix="/app",tags=["Files"])

service=Services()
@api.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail={"message": "No file to upload"})

    path=await service.upload_file(files)
    if not path:
        raise HTTPException(status_code=400, detail={"message": "No file to upload"})
    try:
        add_to_db(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "File upload failed", "error": str(e)})   
    return JSONResponse({"message": "File uploaded successfully", "files": path})


@api.post("/chat",response_model=ChatResponse)
async def User_query(query_data:ChatRequest):
    if query_data is None:
        raise HTTPException(status_code=400, detail={"message": "No query to process"})
    try:
        async def generator():
            try:
                async for result in service.Answer(query_data):
                    yield result
            except Exception as e:
                yield f"Error in processing query: {str(e)}"
        return StreamingResponse(content=generator(),media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})  
    