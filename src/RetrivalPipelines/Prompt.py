from src.Agentic.Retrival_State import RetrivalState

from ..RetrivalPipelines.System_Prompt_Generation import System_query

#System_Query NODE
async def System_Query(state: RetrivalState):
    """System Query Node Function

    This function is responsible for generating optimized queries for
    the hybrid retrieval pipeline. It takes in a RetrivalState object,
    which contains the user query, and returns a dictionary containing
    the optimized semantic, sentactic, and image queries.

    Parameters
    ----------
    state : RetrivalState
        The RetrivalState object containing the user query

    Returns
    -------
    dict
        A dictionary containing the optimized semantic, sentactic, and
        image queries
    """
    try:
        query=state["USER_QUERY"]
        sq = System_query(query)
        await sq.get_system_query()
        return {
            "SEMANTIC_QUERY": sq.Semantic_query,
            "SENTACTIC_QUERY": sq.Sentactic_query,
            "IMAGE_QUERY": sq.Image_query
        }
    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     p=Prompt("What is Langchain?")
#     print(p.get_semantic_query())
#     print(p.get_sentactic_query())
#     print(p.get_image_query())