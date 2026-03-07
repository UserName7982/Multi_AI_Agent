import asyncio
from ..RetrivalPipelines.vectorRetrival import query_result
from collections import defaultdict
from ..RetrivalPipelines.Prompt import System_query
from ..dataIngestionPipelines.SparseIngestion import search_text,get_chunks


class RRF:

    def __init__(self,query:str):
        self.system_query=System_query(query)
        self.dic:defaultdict[str,float]=defaultdict(float)
        self.query=query
        self.Semantic_query: str = ""
        self.Sentactic_query: str = ""
    
    def set_system_querys(self):
        result= self.system_query.get_system_query()
        self.Semantic_query=result["Semantic_prompt"]
        self.Sentactic_query=result["Sentactic_prompt"] 

        
    def get_semantic_result(self,query):
        return query_result(query)

    def get_sentatic_result(self,query):
        return search_text(query, k=7)
    
    def rrf(self, k: int=60):
        self.set_system_querys()
        vector_chunks=self.get_semantic_result(self.Semantic_query)
        sparse_chunks=self.get_sentatic_result(self.Sentactic_query)
        for i,chunk in enumerate(vector_chunks):
            self.dic[chunk["chunk_id"]]+=1/(i+k) 
        
        for i,chunk in enumerate(sparse_chunks):
            self.dic[chunk[0]]+=1/(i+1)
        
        result=sorted(self.dic.items(),key=lambda x:x[1],reverse=True)
        return result
    
    def Hybrid_search(self):
        sorted_Docs= self.rrf()
        n=len(sorted_Docs)
        top_k=min(10,n)
        return get_chunks([doc[0] for doc in sorted_Docs[:top_k]])
    
    
# if __name__ == "__main__":
#     async def run():
#         rrf=RRF("what is langchain")
#         print(await rrf.Hybrid_search())

#     asyncio.run(run())