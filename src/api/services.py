from typing import List
from fastapi import HTTPException, UploadFile
import os
from src.RetrivalPipelines.Retrival import Answer_generation
from ..config import config
FILE_PATH = config.BASE_PATH+"/docs"

class Services:
    result={}
    async def upload_file(self, files: List[UploadFile]):
        os.makedirs(FILE_PATH, exist_ok=True)

        saved: List[dict] = []
        for f in files:
            file_location = os.path.join(FILE_PATH, f.filename) # type: ignore

            content = await f.read()
            with open(file_location, "wb") as out:
                out.write(content)

            saved.append({"filename": f.filename, "path": file_location})

        return saved
    
    async def Answer(self,query):
        try:
            self.result = await Answer_generation(query)
            return self.result
        except Exception as e:
            raise HTTPException(status_code=404, detail={"message": "Error in Generating answer","result":f"{e}","status":404})
   