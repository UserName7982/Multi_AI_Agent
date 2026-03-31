import asyncio
import json
import logging
from typing import AsyncGenerator, List
from fastapi import File, Request, UploadFile,APIRouter,HTTPException,status
from fastapi.responses import JSONResponse, StreamingResponse
from src.dataIngestionPipelines.VectorIngestion import add_to_db
from ..api.schema import ChatRequest,ChatResponse, Thread,Messages, thread_Response,message_Response
from Logger import logger
import json
import traceback
from typing import AsyncGenerator


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




@api.post("/chat", response_model=ChatResponse)
async def User_query(request: Request,query_data: ChatRequest):
    if query_data is None:
        logger.error("No query to process")
        raise HTTPException(status_code=400, detail={"message": "No query to process"})
    async def generator() -> AsyncGenerator[str, None]:
        try:
            async for result in request.app.state.services.Answer(query_data):
                if isinstance(result, str):
                    yield result
                elif isinstance(result, list):
                    yield "".join(
                        item+" " if isinstance(item, str) else json.dumps(item)
                        for item in result
                    )
                elif isinstance(result, dict):
                    yield json.dumps(result)
                else:
                    yield str(result)
        except Exception as e:
            # Log the full traceback to see real error
            logger.error(f"Error in generator:",extra={"error":traceback.format_exc()})
            yield f"Error: {str(e)}"

    try:
        logger.info("Query Answered:",extra={"thread_id":query_data.Thread})
        return StreamingResponse(content=generator(), media_type="text/plain",headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
        "X-Accel-Buffering": "no",
    },)
    except Exception as e:
        logger.error(msg=f"status Code_500 Error in processing query:{traceback.format_exc()}",exc_info=True)
        raise HTTPException(status_code=500, detail={
            "message": "Error in processing query",
            "error": str(e),
            "traceback": traceback.format_exc()
        })

@api.get("/get-threads",response_model=List[Thread])
async def all_get_Thread(request: Request):
    result=await request.app.state.services.all_get_Threads(request)
    return result
@api.get("/get-title/{thread_id}",response_model=List[dict])
async def get_title(request: Request,thread_id:str):
    result= await request.app.state.services.get_title(request,thread_id)
    return result

@api.get("/get-messages/{thread_id}",response_model=List[Messages])
async def get_thread_messages(request: Request,thread_id:str):
    result=await request.app.state.services.get_thread_messages(request,thread_id)
    return result

@api.post("/new-chat",response_model=thread_Response)
async def create_thread(request: Request,thread: Thread):
    result=await request.app.state.services.create_thread(request,thread)
    return JSONResponse({"message": "success","thread_id": result,})

@api.post("/new-message",response_model=List[message_Response])
async def create_message(request: Request,message:List[Messages]):
    result=await request.app.state.services.create_message(request,message)
    return JSONResponse({"message": "success","message_id": result})