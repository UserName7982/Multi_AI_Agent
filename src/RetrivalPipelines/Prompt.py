from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

model = ChatOllama(model="ministral-3:8b", base_url="http://localhost:11434", verbose=True)

class Prompt(BaseModel):
    Sentactic_prompt: str = Field(..., description="Store Syntactic Query for BM25")
    Semantic_prompt: str = Field(..., description="Store Semantic Query for vector search")

parser = PydanticOutputParser(pydantic_object=Prompt)

class System_query:
    def __init__(self, Query: str):
        self.Query = Query
        self.Semantic_query: str = ""
        self.Sentactic_query: str = ""

    def generate_prompt(self):
        System_prompt = """You are a query optimization engine for a hybrid retrieval system (sqlite fts5 + bm25 + vector semantic search).

            Given a user query, produce TWO optimized queries:

            1) Sentactic_prompt (for sqlite fts5 / sparse retrieval)
            - Output ONLY keywords and short phrases.
            -Seperate keywords with OR if they are synonyms or related concepts, otherwise use AND.
            - Include important entities, tool names, error messages, numbers, versions, file names, class/function names.
            - Remove filler words and conversational phrasing.
            - Avoid boolean operators (no OR/AND), avoid quotes, avoid markdown.
            - Add 3–8 helpful synonyms ONLY if they are strongly related and improve recall.
            - Keep it ONE line.

            2) Semantic_prompt (for vector / dense retrieval)
            - Rewrite as a clean, explicit natural-language question.
            - Keep the original meaning, do not add new facts.
            - Include constraints (versions, numbers, errors) explicitly if present.
            - Keep it ONE sentence if possible.

            CRITICAL OUTPUT RULES:
            - Return ONLY valid JSON that matches the schema.
            - No extra keys, no explanations, no markdown, no surrounding text.

            {format_instructions}

            User Query:
            {Query}
            """
        return PromptTemplate.from_template(
            System_prompt,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

    def set_Semantic_query(self, q: str):
        self.Semantic_query = q

    def set_Sentactic_query(self, q: str):
        self.Sentactic_query = q  

    def set_system_query(self):
        chain = self.generate_prompt() | model | parser
        result = chain.invoke({"Query": self.Query})

        self.set_Semantic_query(result.Semantic_prompt)
        self.set_Sentactic_query(result.Sentactic_prompt)

    def get_system_query(self):
        self.set_system_query()
        return {"Sentactic_prompt": self.Sentactic_query, "Semantic_prompt": self.Semantic_query}

sq = System_query("What is Langchain?")
if __name__ == "__main__":
    ans = sq.get_system_query()
    print(ans["Semantic_prompt"], ans["Sentactic_prompt"])