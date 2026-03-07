# # from ..dataIngestionPipelines.VectorIngestion import rank_bm25

# def get_docs():
#     try:
#         documents= rank_bm25.load_docs_data()
#         return documents
#     except Exception as e:
#         print("error in getting the documents",e)

# def sparse_retrival(query_token: list[str]):
#     try:
#         bm25 = rank_bm25.load_bm25()
#         if bm25 is None:
#             raise Exception("BM25 model is not loaded")
#         else:
#             return bm25.get_scores(query_token)
#     except Exception as e:
#         print(e)

# def get_Top_k_docs_id(score,k: int=7):
#     top_idx=sorted(range(len(score)),key=lambda i:score[i],reverse=True)[:k]
#     return top_idx


# # query="What is Langchain?"
# # if __name__ == '__main__':
# #     result=sparse_retrival(create_token(refine_data(query)))
    
# #     if result is not None:
# #         print(get_Top_k_docs_id(result))
# #         print([[wrap_text(doc)] for doc in result])