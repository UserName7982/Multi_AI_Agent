import asyncio
import traceback
from typing import List
import uuid
from fastapi import HTTPException, Request, UploadFile,status
import os
from src.DB.redis import addmessage
from src.api.schema import ChatRequest, Message_Response, Messages, Thread, Thread_Response
from ..config import config
from ..Agentic.Agent import get_graph
from langchain_core.messages import AIMessageChunk, HumanMessage
from Logger import logger

FILE_PATH = config.BASE_PATH + "/docs"

class Services:
    def __init__(self):
        self.workflow = None

    async def initialize(self, pool: dict):
        self.workflow = await get_graph(pool=pool)

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

    async def Answer(self, request: Request, query:ChatRequest):
        cfg = {"configurable": {"thread_id": query.Thread,"user_id":"user"}}
        initial_state = {"messages": [HumanMessage(content=query.query)]}
        # await self.show_state(cfg)
        redis_result=[]
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
                        redis_result.append(event.content)
                        yield event.content
            yield "[END]"
            ai_response="".join(redis_result)
            Message=[Messages(thread_id=query.Thread,role="user",content=query.query),Messages(thread_id=query.Thread,role="ai",content=ai_response)]
            await self.create_message(request,Message)
            logger.info("Answer Generated Successfully",extra={"thread_id": query.Thread})
        except Exception as e:
            logger.error("status_code:500 Error in Answer:\n",extra={"error":traceback.format_exc()})
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
    
    async def all_get_Threads(self,request: Request):
        pool=request.app.state.pools[config.URI]
        if pool is None or pool.closed:
            logger.critical("No pool is open",)
            raise HTTPException(status_code=400, detail={"message": "No pool to create"})
        try:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    logger.info("Start Getting Threads")
                    await cur.execute("SELECT thread_id, user_id, title,created_at FROM threads")
                    rows = await cur.fetchall()
                logger.info("Threads Fetched Successfully")
                formatted = [
                    Thread_Response(
                        user_id=row["user_id"],
                        title=row["title"],
                        thread_id=str(row["thread_id"]),
                        created_at=row["created_at"]
                    )
                    for row in rows
                ]
                return formatted
        except Exception as e:
            logger.error(f"status_code:500 Error in getting Threads in DataBase:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in all_get_Threads", "error": str(e)})
    
    
    async def get_title(self,request: Request,thread_id:uuid.UUID):
        if(await self.check_thread_id_exits(request,thread_id)) is False:
            raise HTTPException(status_code=404, detail={"message": "Thread not found"})
        pool=request.app.state.pools[config.URI]
        if pool is None or pool.closed:
            logger.critical("No pool is open",)
            raise HTTPException(status_code=400, detail={"message": "No pool to create"})
        try:
            async with pool.connection() as conn:
                async with conn.transaction():
                    logger.info("Start Getting title",extra={"thread_id": thread_id})
                    rows=await conn.execute("SELECT title FROM threads Where thread_id=%s",(thread_id,))
                    result=await rows.fetchall()
                return result
        except Exception as e:
            logger.error(f"status_code:500 Error in getting title in DataBase:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in get_title", "error": str(e)})
    
    async def get_thread_messages(self,request: Request,thread_id:uuid.UUID):
        if(await self.check_thread_id_exits(request,thread_id)) is False:
            raise HTTPException(status_code=404, detail={"message": "Thread not found"})
        pool=request.app.state.pools[config.URI]
        if pool is None or pool.closed:
            logger.critical("No pool is open",)
            raise HTTPException(status_code=400, detail={"message": "No pool to create"})
        try:
            async with pool.connection() as conn:
                async with conn.transaction():
                    logger.info("Start Getting messages",extra={"thread_id": thread_id})
                    rows=await conn.execute("SELECT thread_id,role,content,created_at,message_id FROM messages WHERE thread_id=%s",(thread_id,))
                    result=await rows.fetchall()
                    logger.info("Messages Fetched Successfully",extra={"thread_id": thread_id})
                    formatted = [
                        Message_Response(
                            thread_id=str(row["thread_id"]),
                            role=row["role"],
                            content=row["content"],
                            created_at=row["created_at"],
                            message_id=str(row["message_id"])
                        )
                        for row in result
                    ]

            return formatted
        except Exception as e:
            logger.error(f"status_code:500 Error in getting messages in DataBase: {traceback.format_exc()}\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in get_thread_messages", "error": str(e)})
    
    async def create_thread(self,request: Request,thread: Thread):
        if thread is None:
            logger.critical("No thread to create",)
            raise HTTPException(status_code=400, detail={"message": "No thread to create"})
        pool=request.app.state.pools[config.URI]
        if pool is None or pool.closed:
            logger.critical("No pool is open",)
            raise HTTPException(status_code=400, detail={"message": "No pool to create"})
        thread_id=uuid.uuid4()
        title=thread.title
        user_id=thread.user_id
        try:
            async with pool.connection() as conn:
                async with conn.transaction():
                    logger.info("Start Creating thread",extra={"thread_id": thread_id})
                    await conn.execute("INSERT INTO threads (thread_id,title,user_id) VALUES (%s,%s,%s)",(thread_id,title,user_id))
                    logger.info("Thread created Successfully",extra={"thread_id": thread_id})
                    return {"thread_id":thread_id,"title":title}
        except Exception as e:
            logger.error(f"status_code:500 Error in create_thread in DataBase:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in create_thread", "error": str(e)})
    
    async def create_message(self,request: Request,message:List[Messages]):
        pool=request.app.state.pools[config.URI]
        if message is None:
            logger.critical("No message to create",)
            raise HTTPException(status_code=400, detail={"message": "No message to create"})
        try:
            task=[]
            messages=[]
            for msg in message:
                messages.append({
                    "message_id":(uuid.uuid4()),
                    "thread_id":msg.thread_id,
                    "role":msg.role,
                    "content":msg.content
                })
                task.append(addmessage(msg.thread_id,msg.role,msg.content,(messages[-1]["message_id"])))
            await asyncio.gather(*task)
            result=[str(msg["message_id"]) for msg in messages]
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    logger.info("Start Creating message",extra={"thread_id":message[0].thread_id})
                    await cur.executemany("INSERT INTO messages (thread_id,role,content,message_id) VALUES (%s,%s,%s,%s)",((msg["thread_id"],msg["role"] ,msg["content"],msg["message_id"]) for msg in messages))
                    logger.info("Message created Successfully",extra={"thread_id":message[0].thread_id})
                    return result
        except Exception as e:
            logger.error(f"status_code:500 Error in create_message in DataBase:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in create_message", "error": str(e)})
    
    async def delete_chat(self,request: Request,thread_id:uuid.UUID):
        pool=request.app.state.pools[config.URI]
        if pool is None or pool.closed:
            logger.critical("No pool is open",)
            raise HTTPException(status_code=400, detail={"message": "No pool to create"})
        try:
            async with pool.connection() as conn:
                async with conn.transaction():
                    logger.info("Start Deleting thread",extra={"thread_id": thread_id})
                    await conn.execute("DELETE FROM messages WHERE thread_id=%s",(thread_id,))
                    await conn.execute("DELETE FROM threads WHERE thread_id=%s",(thread_id,))
        except Exception as e:
            logger.error(f"status_code:500 Error in delete_thread in DataBase:\n",extra={"error":traceback.format_exc()})
            raise HTTPException(status_code=500, detail={"message": "Error in processing query in delete_thread", "error": str(e)})
    
    async def check_thread_id_exits(self,request: Request,thread_id:uuid.UUID)->bool:
        query="SELECT EXISTS(SELECT 1 FROM threads WHERE thread_id = %s)"
        pool=request.app.state.pools[config.URI]
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query,(thread_id,))
                result=(await cur.fetchone())["exists"]
        return result