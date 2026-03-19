import asyncio
from fastapi import HTTPException
from ..DB.VectorDataBase import tbl,embedding_function

def query_result(text:str,k:int=7):
    try:
        result=  tbl.search(embedding_function.embed_query(text)).limit(k).to_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating vector Search Result: {str(e)}")

# if __name__=="__main__":
#     result=query_result("What is Langchain?")
#     print([r["page_content"] for r in result])