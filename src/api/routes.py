from typing import List
from fastapi import File, UploadFile,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from src.api.services import Services
from src.dataIngestionPipelines.VectorIngestion import add_to_db
from ..api.schema import ChatRequest,ChatResponse
api=APIRouter(prefix="/Files",tags=["Files"])

service=Services()
@api.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    if not files:
        return {"message": "No file to upload"}

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
    try:
        query_= await service.Answer(query_data)
        return {"query":query_data.query,"Answer":query_.get("LLM_RESPONSE")}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})  
    
# @api.get("/image")
# def get_image():
#     return HTMLResponse(f'<img src="data:image/jpeg;base64,{results["base_64_images"][0]}" alt="Image"/>')