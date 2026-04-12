import asyncio
from typing import List
import uuid
from langchain_ollama import ChatOllama, OllamaEmbeddings
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field
from ..Agentic.Tools import rag_retrival,read_emails,send_emails
from langchain_core.messages import HumanMessage, SystemMessage,RemoveMessage,ToolMessage
from langgraph.graph import START,END,StateGraph,MessagesState
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver 
from ..config import config
from langgraph.store.base import BaseStore 
from langgraph.store.postgres.aio import AsyncPostgresStore
from langchain_core.runnables import RunnableConfig

checkpointer = None
workflow = None
short_term_pool=None
long_term_pool=None
store=None


model = ChatOllama(model="ministral-3:8b",verbose=False)
llm=ChatOllama(model="qwen3.5:397b-cloud",base_url="http://localhost:11434",verbose=False)
embedding_function = OllamaEmbeddings(model="embeddinggemma:latest") 


retrival_tools=[rag_retrival,read_emails,send_emails]
llm_with_tools=llm.bind_tools(retrival_tools)
DB_URI = config.DB_URI
DB_URI1=config.DB_URI1


SYSTEM = ("""You are a helpful assistant with memory capabilities and access to tools which contains user knowledge. You are designed to solve user queries by reasoning, planning, and using tools when necessary.

## Objectives
- Understand the user’s intent deeply.
- Break complex problems into smaller steps.
- Use available tools when needed instead of guessing.
- Provide accurate, grounded, and helpful responses.

## Reasoning Strategy
- Think step-by-step before acting.
- If the query requires external data, retrieval, or APIs, decide which tool to use.
- Prefer tool usage over assumptions.
- Combine multiple tool results if needed.

## Tool Usage Rules
- Only call a tool when necessary.
- Always choose the most relevant tool.
- Pass precise and minimal inputs to tools.
- If a tool fails, recover gracefully and try alternatives.
- Never hallucinate tool outputs.

## Retrieval-Augmented Behavior (RAG)
- If context is available, use it as the primary source of truth.
- Do not override retrieved knowledge with assumptions.
- If context is insufficient, say so and optionally ask for clarification.
                       
## Multi-Tool Coordination
- You may:
  - Retrieve documents
  - Call APIs (email, LinkedIn, etc.)
  - Perform calculations
- Combine outputs into a coherent final answer.

## Error Handling
- If a tool returns an error:
  - Explain the issue briefly
  - Retry if possible
  - Ask user for clarification if needed

## Response Style
- Be concise but informative
- Avoid unnecessary verbosity
- Structure responses clearly
- When unsure, ask clarifying questions

## Safety & Constraints
- Do not fabricate facts
- Do not expose internal reasoning unless required
- Respect user privacy and data boundaries

## Memory Management
- Use past interactions if relevant
- Do not assume memory if not explicitly provided

## Execution Mode
You operate in a loop:
1. Understand
2. Plan
3. Act (tool or reasoning)
4. Observe
5. Respond
    
******User_memeory******
## User Details
{user_details_content}
Always aim to minimize steps while maximizing correctness.""")
MEMORY_PROMPT = """You are responsible for updating and maintaining accurate user memory.

CURRENT USER DETAILS (existing memories):
{user_details_content}

TASK:
- Review the user's latest message.
- Extract user-specific info worth storing long-term (identity, stable preferences, ongoing projects/goals).
- For each extracted item, set is_new=true ONLY if it adds NEW information compared to CURRENT USER DETAILS.
- If it is basically the same meaning as something already present, set is_new=false.
- Keep each memory as a short atomic sentence.
- No speculation; only facts stated by the user.
- If there is nothing memory-worthy, return should_write=false and an empty list.
"""
class chatmessage(MessagesState):
    summary:str
    emails:dict|None
    draft_email:dict|None

async def get_checkpointer(pool:AsyncConnectionPool):
    checkpointer = AsyncPostgresSaver(conn=pool) # type: ignore
    await checkpointer.setup()
    return checkpointer

async def get_store(pool:AsyncConnectionPool):
    store = AsyncPostgresStore(conn=pool,index={"embed":embedding_function,"dims":768}) # type: ignore
    print('store setup successfully')
    await store.setup()
    print("=== store setup complete ===")
    return store

async def summarized_conversation(state: chatmessage):
    """
    Summarize the conversation above.

    If there is an existing summary, prompt the model to extend it.
    Otherwise, prompt the model to summarize the conversation from scratch.

    Returns a state update with the new summary and the messages to be deleted.
    """
    existing_summary = state.get("summary","")
    if existing_summary:
        prompt = (
            f"Existing summary:\n{existing_summary}\n\n"
            "Extend the summary using the new conversation above."
        )
    else:
        prompt = "Summarize the conversation above."
    summarize_message=state["messages"]+[HumanMessage(content=prompt)]
    response=await llm.ainvoke(summarize_message)
    message_delete=state["messages"][:-2]
    return {"summary":response.content,"messages":[RemoveMessage(id=msg.id) for msg in message_delete]} # type: ignore

async def do_summarize(state: chatmessage):
    return len(state["messages"])>6

graph=StateGraph(chatmessage)

async def chat_node(state:chatmessage,config:RunnableConfig,*,store: BaseStore):
    """
    The chat node is the main entry point for the user to interact with the AI.
    
    It takes the last message from the user, searches for relevant memories from the user's memory,
    and then passes the concatenated messages to the LLM to generate a response.
    
    The chat node returns the new message from the LLM in the "messages" key of the state.
    """
    user_id=(config["configurable"]["user_id"]) # type: ignore
    ns=("user",user_id,"details")

    last_message=state["messages"][-1].content
    memories = await store.asearch( # type: ignore
        ns,
        query=last_message, # type: ignore
        limit=3
    )
    existing_memories="\n".join(it.value.get("data", "") for it in memories) if memories else "(empty)"
    messages=[SystemMessage(content=SYSTEM.format(user_details_content=existing_memories))]+state["messages"]
    response=await llm_with_tools.ainvoke(messages)
    return {"messages":[response]}

class MemoryItem(BaseModel):
    text: str = Field(description="Atomic user memory")
    is_new: bool = Field(description="True if new, false if duplicate")

class MemoryDecision(BaseModel):
    should_write: bool = Field(description="True if message should be written to memory")
    memories: List[MemoryItem] = Field(default_factory=list)

memory_extractor = model.with_structured_output(MemoryDecision)


async def remember_node(state: chatmessage,config:RunnableConfig,*,store: BaseStore):
    user_id=(config["configurable"]["user_id"]) # type: ignore
    ns=("user",user_id,"details")

    last_message=state["messages"][-1].content
    memories = await store.asearch( # type: ignore
        ns,
        query=last_message, # type: ignore
        limit=3
    )
    existing_memories="\n".join(it.value.get("data", "") for it in memories) if memories else "(empty)"
    decision: MemoryDecision = await memory_extractor.ainvoke([
            SystemMessage(content=MEMORY_PROMPT.format(user_details_content=existing_memories)),
            {"role": "user", "content": last_message},
        ]) # type: ignore
    # print("existing_memories:",existing_memories)
    key=str(uuid.uuid4())
    if decision.should_write:
        for msg in decision.memories:
            if msg.is_new:
                await store.aput( # type: ignore
                    ns,
                    key,
                    {"data": msg.text},
                )
    return {}
        
async def tool_node(state: chatmessage):
    last_message=state["messages"][-1]
    tool_results=[]
    for tool_call in last_message.tool_calls: # type: ignore
        for tools in retrival_tools:
            if tools.name == tool_call["name"]:
                result=await tools.ainvoke(tool_call["args"])
                tool_results.append(ToolMessage(content=result,tool_call_id=tool_call["id"]))
                print("tool_results",tool_results)
    return {"messages":tool_results}

async def route_after_chat(state: chatmessage):
    lastMessage=state["messages"][-1]
    if hasattr(lastMessage,"tool_calls") and lastMessage.tool_calls: # type: ignore
        return "tools"
    if(await do_summarize(state)):
        return "summarize"
    return END

graph.add_node("chat_node",chat_node)
graph.add_node("remember",remember_node)
graph.add_node("tools",tool_node)
graph.add_node("summarize",summarized_conversation)
graph.add_edge(START,"remember")
graph.add_edge("remember","chat_node")
graph.add_edge("tools","chat_node")
graph.add_conditional_edges("chat_node",route_after_chat,{
    "tools": "tools",
    "summarize": "summarize",
    END: END,
})
graph.add_edge("summarize",END)

lock = asyncio.Lock()
async def get_graph(pool):
    global checkpointer, workflow, short_term_pool, long_term_pool, store
    if workflow is None:
        async with lock:
            short_term_pool = pool[DB_URI]
            long_term_pool = pool[DB_URI1]
            checkpointer = await get_checkpointer(pool=short_term_pool)
            store = await get_store(pool=long_term_pool)
            workflow = graph.compile(checkpointer=checkpointer, store=store)
    return workflow