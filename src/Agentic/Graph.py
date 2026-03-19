from langgraph.graph import StateGraph,START,END
from ..Agentic.Retrival_State import RetrivalState
from ..RetrivalPipelines.Prompt import System_Query
from ..RetrivalPipelines.Retrival import Answer_Query

graph=StateGraph(RetrivalState)

def error(state: RetrivalState):
    if state.get("error"):
        raise Exception(state["error"])
    return END

graph.add_node("System_Query",System_Query)
graph.add_node("Answer_Query",Answer_Query)
graph.add_node("Error",error)

graph.add_edge(START,"System_Query")
graph.add_edge("System_Query","Answer_Query")
graph.add_conditional_edges("Answer_Query",error)

workflow=graph.compile()
