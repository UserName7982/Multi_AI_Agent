from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from ..RetrivalPipelines.RRF import RRF
from langchain_core.output_parsers import StrOutputParser

model=ChatOllama(model="qwen3.5:397b-cloud",base_url="http://localhost:11434",verbose=True)
prompt=PromptTemplate.from_template("You are a helpful assistant. Answer the given query only from the given context./n *******Query******/n {query} /n******{context}******")
parser=StrOutputParser()

async def Answer_generation(text:str):
    rrf=RRF(text)
    try:
        chain= prompt | model | parser
        chunks=rrf.Hybrid_search()
        result=await chain.ainvoke({"query":text,"context":chunks})
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating answer: {str(e)}")