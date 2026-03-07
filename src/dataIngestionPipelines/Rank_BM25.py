# import json
# import os
# import pickle
# from typing import List, Dict, Optional
# from rank_bm25 import BM25Okapi


# class RankBM25Store:
#     def __init__(self, bm25_dir: str):
#         self.bm25_dir = bm25_dir

#         # file paths
#         self.tokens_path = os.path.join(bm25_dir, "tokens.json")
#         self.docs_path = os.path.join(bm25_dir, "docs.json")
#         self.meta_path = os.path.join(bm25_dir, "meta.json")
#         self.pickle_path = os.path.join(bm25_dir, "bm25.pkl")
#         self.ids_path = os.path.join(bm25_dir, "ids.json")

#         os.makedirs(self.bm25_dir, exist_ok=True)

#         # in-memory state
#         self.tokens: List[List[str]] = []
#         self.texts: List[str] = []
#         self.metadatas: List[dict] = []
#         self.ids: List[str] = []
#         self.id2idx: Dict[str, int] = {}

#         # BM25 model (in RAM)
#         self.bm25: Optional[BM25Okapi] = None
    
#     def load_bm25(self):
#         if os.path.exists(self.pickle_path):
#             with open(self.pickle_path, "rb") as f:
#                 self.bm25 = pickle.load(f)
#             if self.bm25 is None:
#                 self.bm25 = BM25Okapi(self.load_token_data())
#         return self.bm25
#     def load_token_data(self):
#         if os.path.exists(self.tokens_path):
#             with open(self.tokens_path,'r') as f:
#                 self.tokens = json.load(f)
#         return self.tokens
    
#     def load_meta_data(self):
#         if os.path.exists(self.meta_path):
#             with open(self.meta_path,'r') as f:
#                 self.metadatas = json.load(f)
#         return self.metadatas
    
#     def load_text_data(self):
#         if os.path.exists(self.docs_path):
#             with open(self.docs_path,'r') as f:
#                 self.texts = json.load(f)
#         return self.texts
    
#     def load_docs_data(self):
#         if os.path.exists(self.docs_path):
#             with open(self.docs_path,'r') as f:
#                 self.docs = json.load(f)
#         return self.docs
    
#     def load_ids(self):
#         if os.path.exists(self.ids_path):
#             with open(self.ids_path,'r') as f:
#                 self.ids = json.load(f)
#         return self.ids

# def write_data_to_pickle(data:BM25Okapi,path: str):
#     """write data->bm25 to pickle file"""
#     try:
#         with open(path, "wb") as f:
#             pickle.dump(data, f)
#     except Exception as e:
#         print(e)
        
# def write_tokens_to_json(data,path):
#     """write data->tokens to json file"""
#     with open(path, "w") as f:
#         json.dump(data, f,indent=2)
  
# def write_data_to_json(data, path):
#         """write data->docs to json file"""
#         with open(path, "w") as f:
#             json.dump(data, f,indent=2)

# def write_ids_to_json(data, path):
#         """write data->ids to json file"""
#         with open(path, "w") as f:
#             json.dump(data, f,indent=2)