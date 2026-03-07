import sqlite3

db=sqlite3.connect("sparse.db")

table=db.execute('''CREATE TABLE IF NOT EXISTS CHUNKS
             (chunk_id TEXt NOT NULL PRIMARY KEY,
             chunk_index INTEGER NOT NULL,
             chunk TEXT NOT NULL,
             source TEXT NOT NULL);''')

fts_table=db.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS CHUNKS_FTS USING fts5(chunk_id,content);''')