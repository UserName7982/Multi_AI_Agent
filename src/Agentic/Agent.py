from langchain_ollama import ChatOllama
from ..Agentic.Tools import rag_retrival
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START,END,StateGraph

llm=ChatOllama(model="qwen3.5:397b-cloud",base_url="http://localhost:11434",verbose=False)
retrival_tools=[rag_retrival]
llm_with_tools=llm.bind_tools(retrival_tools)

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

class chatmessage(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


graph=StateGraph(chatmessage)

def chat_node(state:chatmessage):
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
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}

tools=ToolNode(tools=retrival_tools)

graph.add_node("chat_node",chat_node)
graph.add_node("tools",tools)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

workflow=graph.compile()
