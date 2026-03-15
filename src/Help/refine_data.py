import string
import re
def refine_data(text):
    query=re.sub(r"[^\w\s]", " ", text)
    query = re.sub(r"\s+", " ", query).strip()
    return query

def create_token(chunk: str):
    return chunk.split(" ")

if __name__ == "__main__":
    text='Bahadur Shah Zafar AND (1857-1858) AND "Captain Hodson"'
    refined_text=refine_data(text)
    print(refined_text)
    # tokens=create_token(refined_text)
    # print(tokens)