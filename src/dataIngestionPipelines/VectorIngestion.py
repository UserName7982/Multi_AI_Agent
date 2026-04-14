from collections.abc import Iterable
import hashlib
from fastapi import HTTPException
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
# from .BM25Store import RankBM25Store
# from src.dataIngestionPipelines.refine_data import refine_data,create_token
# from rank_bm25 import BM25Okapi
from ..DB.VectorDataBase import embedding_function
from ..DB.VectorDataBase import tbl
from ..dataIngestionPipelines.SparseIngestion import ingest_chunk_into_db
# from ..dataIngestionPipelines.Images_Ingestion import Ingest_images_from_pdf

# rank_bm25 = RankBM25Store("bm25")

textsplitter=RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=20, length_function=len)


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_pdf(path:str) -> Iterable[Document]:
    for d in PyPDFLoader(path).lazy_load():
        yield d
def load_text(path:str) -> Iterable[Document]:
    for d in TextLoader(path).lazy_load():
        yield d

def store_in_db(chunks: List[Document]):
    row=[]
    
    for c in chunks:
        vec=embedding_function.embed_query(c.page_content)
        row.append({
            "chunk_id": c.metadata.get("chunk_id"),
            "vector": [float(v) for v in vec],
            "page_content": c.page_content,
            "source": c.metadata.get("source"),
            "chunk_index": c.metadata.get("chunk_index"),
            "chunk_hash": c.metadata.get("chunk_hash")
        })
    tbl.add(row)

def split_and_enrich(docs: Iterable[Document]) -> List[Document]:
    docs = list(docs)

    for d in docs:
        src = d.metadata.get("source", "unknown")
        d.metadata["source"] = src

    chunks = textsplitter.split_documents(docs)  
    
    for i, c in enumerate(chunks):
        src = c.metadata.get("source", "unknown")
        chunk_hash = sha256_text(c.page_content)
        c.metadata["chunk_index"] = i
        c.metadata["chunk_hash"] = chunk_hash
        c.metadata["chunk_id"] = f"{src}:{chunk_hash}:{i}"
        ingest_chunk_into_db(c.metadata["chunk_id"], i, c.page_content, src)
          # Store each chunk in the database immediately after processing
    return chunks

# def Store_bm25(chunks: List[Document]):
#     rank_bm25.texts=[c.page_content for c in chunks]
#     rank_bm25.tokens=[create_token(refine_data(c.page_content)) for c in chunks]

#     write_data_to_json(rank_bm25.texts, rank_bm25.docs_path)
#     write_ids_to_json([c.metadata.get("chunk_id") for c in chunks], rank_bm25.ids_path)
#     write_tokens_to_json(rank_bm25.tokens, rank_bm25.tokens_path)
#     write_data_to_pickle(BM25Okapi(rank_bm25.tokens), rank_bm25.pickle_path)


def add_to_db(Docs_Path: List[dict]):

    for Path in Docs_Path:
        try:
            docs=[]
            file_path=Path["path"]
            if file_path.endswith(".pdf"):
                docs=load_pdf(file_path)
                # Ingest_images_from_pdf(file_path)
            elif file_path.endswith(".txt"):
                docs=load_text(file_path)
            chunks = split_and_enrich(docs)
            store_in_db(chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {Path['path']}: {str(e)}")

    return {"status": "success", "message": "Data added to database"}