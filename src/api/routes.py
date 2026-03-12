from typing import List
from fastapi import File, UploadFile,APIRouter,HTTPException
from fastapi.responses import JSONResponse,HTMLResponse
from src.api.services import Services
from src.dataIngestionPipelines.VectorIngestion import add_to_db

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

@api.post("/Query/{query}")
async def User_query(query:str):
    try:
        query_= await service.Answer(query)
        return JSONResponse({"message":"query_executed_sucessfully","Image_result":f"{query_['image_result']}","Text_result":f"{query_['text_result']}","status":200})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})  
    
# @api.get("/image")
# def get_image():
#     return HTMLResponse(f'<img src="data:image/jpeg;base64,{results["base_64_images"][0]}" alt="Image"/>')