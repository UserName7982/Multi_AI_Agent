from ..RetrivalPipelines.System_Prompt_Generation import System_query

class Prompt:
    def __init__(self,query:str):
        self.prompt=System_query(Query=query)
        self.prompt()
        
    def get_semantic_query(self):
        return self.prompt.Semantic_query
    
    def get_sentactic_query(self):
        return self.prompt.Sentactic_query
    
    def get_image_query(self):
        return self.prompt.Image_query

# if __name__ == "__main__":
#     p=Prompt("What is Langchain?")
#     print(p.get_semantic_query())
#     print(p.get_sentactic_query())
#     print(p.get_image_query())