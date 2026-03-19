import string
import re
def refine_data(text):
    return clean_term(text)
     
def create_token(chunk: str):
    return chunk.split(" ")

def clean_term(term: str) -> str:
    term = term.replace("\\'", " ").replace('\\"', " ")
    term = term.replace("'", " ")
    term = re.sub(r"[(){}\[\],;:!?@#$%^&*=+<>/~`|\\-]", " ", term)
    term = re.sub(r'[^A-Za-z0-9\s]', " ", term)
    term = re.sub(r"\s+", " ", term).strip()
    return term

# def build_fts5_or_query(terms: list[str]) -> str:
#     cleaned = []
#     for term in terms:
#         t = clean_term(term)
#         if not t:
#             continue
#         if " " in t:
#             cleaned.append(f'"{t}"')
#         else:
#             cleaned.append(t)
#     return " OR ".join(cleaned)

if __name__ == "__main__":
    text=" \\'project set OR project configuration OR deployment setup AND \\'Harsh Resume\\' AND \\'get it\\' AND \\'resume parser\\' AND \\'resume extraction\\' AND \\'resume automation\\' AND \\'resume data retrieval\\' AND \\'resume processing\\' AND \\'resume template\\' AND \\'resume file\\' AND \\'resume format\\'\\': fts5: syntax error near \"\\'\""
    refined_text=refine_data(text)
    print(refined_text)
    # tokens=create_token(refined_text)
    # print(tokens)