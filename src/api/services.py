from typing import List
from fastapi import HTTPException, UploadFile
import os
from ..config import config
from ..Agentic.Agent import workflow
from langchain.messages import AIMessage, AIMessageChunk, HumanMessage

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
    
    async def Answer(self, query):
        cfg = {"configurable": {"thread_id": query.Thread}}  # 
        initial_state = {"messages": [HumanMessage(content=query.query)]}
        
        try:
            async for result in workflow.astream(
                input=initial_state, # type: ignore
                config=cfg, # type: ignore
                stream_mode="updates"
            ):
                if "chat_node" in result:
                    for msg in result["chat_node"].get("messages", []):
                        if (
                            isinstance(msg, AIMessage)
                            and msg.content
                            and not msg.tool_calls
                        ):
                            yield msg.content
            yield "Done"
        except Exception as e:
            yield f"Error in processing query: {str(e)}"
            raise HTTPException(
                status_code=500,
                detail={"message": "Error in processing query", "error": str(e)}
            )