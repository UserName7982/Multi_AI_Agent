import asyncio
from typing import Annotated, cast

from langchain_ollama import ChatOllama
import psycopg
from ..Agentic.Tools import rag_retrival
from langchain_core.messages import HumanMessage, SystemMessage,RemoveMessage,ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START,END,StateGraph,MessagesState
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver 
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row

llm=ChatOllama(model="qwen3.5:397b-cloud",base_url="http://localhost:11434",verbose=False)
retrival_tools=[rag_retrival]
llm_with_tools=llm.bind_tools(retrival_tools)
DB_URI = f"postgresql://postgres:admin@localhost:5432/chatsummary"

SYSTEM = SystemMessage(content="""You are an intelligent, autonomous AI agent designed to solve user queries by reasoning, planning, and using tools when necessary.

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

## Memory (if available)
- Use past interactions if relevant
- Do not assume memory if not explicitly provided

## Execution Mode
You operate in a loop:
1. Understand
2. Plan
3. Act (tool or reasoning)
4. Observe
5. Respond

Always aim to minimize steps while maximizing correctness.""")

class chatmessage(MessagesState):
    summary:str


async def get_checkpointer():
    conn = cast(
        AsyncConnection[DictRow],
        await AsyncConnection.connect(
            "postgresql://postgres:admin@localhost:5432/chatsummary",
            row_factory=dict_row # type: ignore
            ,autocommit=True
        )
    )
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()
    return checkpointer

async def summarized_conversation(state: chatmessage):
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

async def chat_node(state:chatmessage):
    """
    This function takes in a chatmessage state and uses the LLM to generate a response based on the messages in the state.

    Parameters
    ----------
    state : chatmessage
        The chatmessage state containing the messages to be processed.

    Returns
    -------
    dict
        A dictionary containing the response from the LLM.

    """
    messages=[SYSTEM]+state["messages"]
    response=await llm_with_tools.ainvoke(messages)
    print(state["messages"])
    return {"messages":[response]}

tools=ToolNode(tools=retrival_tools)

async def tool_node(state: chatmessage):
    last_message=state["messages"][-1]
    tool_results=[]
    for tool_call in last_message.tool_calls: # type: ignore
        for tools in retrival_tools:
            if tools.name == tool_call["name"]:
                result=await tools.ainvoke(tool_call["args"])
                tool_results.append(ToolMessage(content=result,tool_call_id=tool_call["id"]))
    return {"messages":tool_results}

async def route_after_chat(state: chatmessage):
    lastMessage=state["messages"][-1]
    if hasattr(lastMessage,"tool_calls") and lastMessage.tool_calls: # type: ignore
        return "tools"
    if(await do_summarize(state)):
        return "summarize"
    return END

graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node)
graph.add_node("summarize",summarized_conversation)
graph.add_edge(START,"chat_node")
graph.add_edge("tools","chat_node")
graph.add_conditional_edges("chat_node",route_after_chat,{
    "tools": "tools",
    "summarize": "summarize",
    END: END,
})
graph.add_edge("summarize",END)


checkpointer = None
workflow = None

async def get_graph():
    global checkpointer, workflow
    if workflow is None:
        checkpointer = await get_checkpointer()
        workflow = graph.compile(checkpointer=checkpointer)
    return workflow
