from typing import List
from fastapi import HTTPException, UploadFile
import os
from ..config import config
from ..Agentic.Graph import workflow

FILE_PATH = config.BASE_PATH+"/docs"

class Services:
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
        if query is None:
           raise HTTPException(status_code=400, detail={"message": "No query to process"} )
        try:
           initial_state={"USER_QUERY":query.query}
           config={"Configurable":{"Thread":query.Thread}}
           result=await workflow.ainvoke(initial_state) # type: ignore
           return result
        except Exception as e:
            raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})