import logging
import traceback
from typing import List
from fastapi import UploadFile
import os
from ..config import config
from ..Agentic.Agent import get_graph
from langchain_core.messages import AIMessage, HumanMessage

FILE_PATH = config.BASE_PATH + "/docs"
logger = logging.getLogger(__name__)

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
        cfg = {"configurable": {"thread_id": query.Thread}}
        initial_state = {"messages": [HumanMessage(content=query.query)]}

        if self.workflow is None:
            yield "Workflow is not initialized"
            return 
        await self.show_state(cfg)
        try:
            async for result in self.workflow.astream(
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
            logger.error(f"Error in Answer:\n{traceback.format_exc()}")
            yield f"Error in processing query: {str(e)}"

    async def show_state(self,config):
        snap =await self.workflow.aget_state(config) # type: ignore
        vals = snap.values
        print("\n--- STATE ---")
        print("summary:", vals.get("summary", ""))
        print("num_messages:", len(vals.get("messages", [])))
        print("messages:")
        for m in vals.get("messages", []):
            print("-", type(m).__name__, ":", m.content[:80])