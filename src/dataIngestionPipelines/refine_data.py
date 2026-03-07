import string

def refine_data(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower()

def create_token(chunk: str):
    return chunk.split(" ")