import traceback
from typing import List
from fastapi import HTTPException, UploadFile,status
import os
from ..config import config
from ..Agentic.Agent import get_graph
from langchain_core.messages import AIMessageChunk, HumanMessage
from Logger import logger

FILE_PATH = config.BASE_PATH + "/docs"

class Services:
    def __init__(self):
        self.workflow = None

    async def initialize(self):
        self.workflow = await get_graph()

    async def upload_file(self, files: List[UploadFile]):
        os.makedirs(FILE_PATH, exist_ok=True)
        saved: List[dict] = []
        for f in files:
            file_location = os.path.join(FILE_PATH, f.filename)  # type: ignore
            content = await f.read()
            with open(file_location, "wb") as out:
                out.write(content)
            saved.append({"filename": f.filename, "path": file_location})
        return saved

    async def Answer(self, query):
        cfg = {"configurable": {"thread_id": query.Thread,"user_id":"user1"}}
        initial_state = {"messages": [HumanMessage(content=query.query)]}
        # await self.show_state(cfg)
        if self.workflow is None:
            yield "Workflow is not initialized"
            return 
        try:
            async for result in self.workflow.astream(
                input=initial_state, # type: ignore
                config=cfg, # type: ignore
                stream_mode="messages"
            ):
                # print(result)
                event,metadata=result
                if (isinstance(event, AIMessageChunk)
                        and event.content and (metadata.get("langgraph_node","") == "chat_node") # type: ignore
                        and  not event.tool_calls):
                        yield event.content
            yield "[END]"
            logger.info("Answer completed",extra={"thread_id": query.Thread})
        except Exception as e:
            logger.error(f"status_code:500 Error in Answer:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in Answer", "error": str(e)})

    async def show_state(self,config):
        snap =await self.workflow.aget_state(config) # type: ignore
        vals = snap.values
        print("\n--- STATE ---")
        print("summary:", vals.get("summary", ""))
        print("num_messages:", len(vals.get("messages", [])))
        print("messages:")
        for m in vals.get("messages", []):
            print("-", type(m).__name__, ":", m.content[:80])
    