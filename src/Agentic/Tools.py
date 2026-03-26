from fastapi import HTTPException

from ..Agentic.Graph import workflow
from langchain_core.tools import tool

@tool(description="""This tool get user documents and performs hybrid retrieval (semantic + BM25) over indexed content and generates answers using LLMs.""")
async def rag_retrival(query: str,Thread: int = 1):
    """
    This tool performs hybrid retrieval (semantic + BM25) over indexed content and generates answers using LLMs.

    Parameters
    ----------
    query : Query
        The query object containing the user query, thread, and other relevant information.

    Returns
    -------
    result : str
        The generated answer.
    """
    try:
        config={"configurable": {"thread_id": Thread}}
        initial_state={"USER_QUERY":query}
        result=await workflow.ainvoke(initial_state,config=config) # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})
    return result.get('LLM_RESPONSE','')