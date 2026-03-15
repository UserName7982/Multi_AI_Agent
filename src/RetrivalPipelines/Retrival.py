import asyncio
from ..Help.refine_data import refine_data
from langchain_core.output_parsers import JsonOutputParser
from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from .RRF import RRF
from langchain_core.output_parsers import StrOutputParser
from .Prompt import Prompt
from .ImageRetriver import convert_images_to_base64
# from langchain_core.runnables import RunnableParallel
# from langchain_google_genai import GoogleGenerativeAI
from ..config import config
# parser2 = JsonOutputParser()

# model1=GoogleGenerativeAI(model="gemini-3-flash-preview",temperature=0.7,api_key=config.Gemini_API_KEY,verbose=True)
model=ChatOllama(model="qwen3.5:397b-cloud",base_url="http://localhost:11434",verbose=True)
text_prompt=PromptTemplate.from_template("You are a helpful assistant. Answer the given query only from the given context./n *******Query******/n {query} /n******{context}******")
parser1=StrOutputParser()
# image_prompt="""You are a multimodal assistant.

#         You will receive:
#         1. A user query
#         2. An Array of images in base64 format with some metadata (image_id, doc name, page number)

#         Your task is to determine how relevant the image is to the user query.

#         Steps:
#         1. Understand the user query.
#         2. Analyze the image and identify objects, diagrams, text, or visual concepts.
#         3. Compare the image with the query and context.
#         4. Determine how relevant the image is.

#         Return ONLY valid JSON in the following format:

#         {{
#         "image_id": "<exact image_id provided in input>",
#         "doc": "<exact document name>",
#         "page": <exact page number>,
#         "query": "<user query>",
#         "image_description": "<short description of the image>",
#         "relevance": "high | medium | low | not_relevant",
#         "relevance_score": 0-1,
#         "confidence": 0-1,
#         "reason": "<short explanation>"
#         }}

#         {format_instructions}

#         Rules:
#         - relevance_score measures how related the image is to the query.
#         - confidence measures how confident you are in the judgment.
#         - If the image has no relation to the query, return relevance = "not_relevant".
#         - Output must be valid JSON only.
#         *********Query********
#         {image_query}
#         ************************
#         *********Context********
#         {image_context}
#         """
# image_prompt_template=PromptTemplate.from_template(image_prompt,partial_variables={"format_instructions": parser2.get_format_instructions()})


async def Answer_generation(text:str):
    _prompt=Prompt(text)
    sentactic_query=_prompt.get_sentactic_query()
    semantic_query=_prompt.get_semantic_query()
    rrf=RRF(refine_data(semantic_query), sentactic_query)
    try:
        chain1= text_prompt | model | parser1
        chunks=rrf.Hybrid_search()
        result= chain1.invoke({"query":text,"context":chunks})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating answer: {str(e)}")
    

# async def Multi_Retrival(text:str):
#     _prompt=Prompt(text)
#     sentactic_query=_prompt.get_sentactic_query()
#     semantic_query=_prompt.get_semantic_query()
#     image_query=_prompt.get_image_query()
#     image_context=convert_images_to_base64(image_query,3)
#     rrf=RRF(semantic_query, sentactic_query)
#     try:
#         chain1= text_prompt | model | parser1
#         chain2=image_prompt_template | model1 | parser2
#         chunks=rrf.Hybrid_search()
#         final_chain=RunnableParallel({"text_result": chain1, "image_result": chain2})
#         result= final_chain.invoke({"query":text,"context":chunks,"image_query":image_query,"image_context":image_context})
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in generating answer: {str(e)}")
    
# if __name__ == "__main__":
#     query = "Who was the last powerful Mughal ruler mentioned in the text?"
#     answer =asyncio.run(Answer_generation(query))
#     print(answer)