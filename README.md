Personal AI Knowledge Assistant

A local-first, privacy-focused AI system that allows users to upload and query their personal knowledge using a multi-model Retrieval Augmented Generation (RAG) pipeline.

The assistant performs hybrid retrieval (Semantic + BM25) over indexed content and generates answers using LLMs. It supports text and image understanding, PDF ingestion, and integrates email and LinkedIn management features.

The system follows a sidecar-based architecture where indexing and retrieval happen locally to ensure data privacy and fast search performance.

Features

📄 Document Understanding – Upload and query PDFs and documents

🖼 Image Understanding – Extract and embed images from PDFs

🔍 Hybrid Search – Combines vector search + BM25 sparse search

🤖 RAG Pipeline – Uses retrieved context to generate accurate answers

📬 Email Management – AI assistance for handling emails

💼 LinkedIn Management – Tools for professional networking automation

🔐 Privacy Focused – Local indexing using sidecar architecture

⚡ Fast Retrieval – Optimized pipelines for large document collections

Tech Stack

Backend: FastAPI

LLM: Ollama / Cloud Models

Vector Database: LanceDB / Chroma

Sparse Search: SQLite FTS5 / BM25

Embedding Models: OpenCLIP / Text Embedding Models

Language: Python

Architecture Overview

The system uses a Hybrid RAG Architecture:

Data Ingestion

Extract text and images

Generate embeddings

Store data in vector and sparse databases

Hybrid Retrieval

Semantic search (vector embeddings)

Sparse search (BM25)

Combine results using Reciprocal Rank Fusion (RRF)

Answer Generation

Retrieve relevant context

Pass context to LLM

Generate final response

Current Project Structure

'
src
 ┣ api
 ┃ ┣ __pycache__
 ┃ ┃ ┣ routes.cpython-311.pyc
 ┃ ┃ ┗ services.cpython-311.pyc
 ┃ ┣ routes.py
 ┃ ┗ services.py
 ┣ dataIngestionPipelines
 ┃ ┣ __pycache__
 ┃ ┃ ┣ chroma.cpython-311.pyc
 ┃ ┃ ┣ dataIngestion.cpython-311.pyc
 ┃ ┃ ┣ Images_Ingestion.cpython-311.pyc
 ┃ ┃ ┣ Rank_BM25.cpython-311.pyc
 ┃ ┃ ┣ refine_data.cpython-311.pyc
 ┃ ┃ ┣ SparseIngestion.cpython-311.pyc
 ┃ ┃ ┣ TextIngestion.cpython-311.pyc
 ┃ ┃ ┗ VectorIngestion.cpython-311.pyc
 ┃ ┣ Images_Ingestion.py
 ┃ ┣ Rank_BM25.py
 ┃ ┣ refine_data.py
 ┃ ┣ SparseIngestion.py
 ┃ ┗ VectorIngestion.py
 ┣ DB
 ┃ ┣ __pycache__
 ┃ ┃ ┣ SparseDataBase.cpython-311.pyc
 ┃ ┃ ┗ VectorDataBase.cpython-311.pyc
 ┃ ┣ SparseDataBase.py
 ┃ ┗ VectorDataBase.py
 ┣ RetrivalPipelines
 ┃ ┣ __pycache__
 ┃ ┃ ┣ ImageRetriver.cpython-311.pyc
 ┃ ┃ ┣ Model.cpython-311.pyc
 ┃ ┃ ┣ Prompt.cpython-311.pyc
 ┃ ┃ ┣ Retirval.cpython-311.pyc
 ┃ ┃ ┣ RRF.cpython-311.pyc
 ┃ ┃ ┣ SparseRetrival.cpython-311.pyc
 ┃ ┃ ┗ vectorRetrival.cpython-311.pyc
 ┃ ┣ ImageRetriver.py
 ┃ ┣ Prompt.py
 ┃ ┣ Retirval.py
 ┃ ┣ RRF.py
 ┃ ┣ SparseRetrival.py
 ┃ ┗ vectorRetrival.py
 ┣ __pycache__
 ┃ ┣ config.cpython-311.pyc
 ┃ ┗ __init__.cpython-311.pyc
 ┣ config.py
 ┗ __init__.py
 '