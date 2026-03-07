from fastapi import HTTPException
from typing import List
from ..DB.SparseDataBase import table

conn=table.connection
def ingest_chunk_into_db(chunk_id,chunk_index,chunk,source):
    try:
        with conn:
            conn.execute("INSERT INTO CHUNKS (chunk_id, chunk_index, chunk, Source) VALUES (?, ?, ?, ?)",
                        (chunk_id, chunk_index, chunk, source))
            conn.execute("INSERT INTO CHUNKS_FTS (chunk_id, content) VALUES (?, ?)",
                            (chunk_id, chunk))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting chunk into database {chunk_id}: {str(e)}")
    

def search_text(query: str, k: int = 5):
    try:
       with conn:
        cur = conn.execute("""
            SELECT chunk_id, content, bm25(CHUNKS_FTS) AS score
            FROM CHUNKS_FTS
            WHERE CHUNKS_FTS MATCH ?
            ORDER BY score
            LIMIT ?;
            """, (query, k))
        return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for query '{query}': {str(e)}")

def get_chunks(list_of_chunk_ids:List[str]):
    try:
        with conn:
            placeholders = ','.join('?' * len(list_of_chunk_ids))
            cur = conn.execute(f"SELECT chunk_id, chunk FROM CHUNKS WHERE chunk_id IN ({placeholders})", list_of_chunk_ids)

            result= cur.fetchall()
            chunks="\n".join([chunk[1] for chunk in result])
            return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks: {str(e)}")
    

if __name__ == "__main__":
    # chunk_id = "test_chunk_3"
    # chunk_index = 0
    # chunk = "hybrid search combines the strengths of both vector and sparse search methods, providing a more comprehensive and effective search experience."
    # ingest_chunk_into_db(chunk_id, chunk_index, chunk, "test_source")
    # print("Chunk ingested successfully.")
    results = search_text("Langchain", k=5)
    chunks = get_chunks([result[0] for result in results])
    print("Search results:", chunks)