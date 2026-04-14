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

```
📦src
 ┣ 📂Agentic
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜Agent.cpython-311.pyc
 ┃ ┃ ┣ 📜Graph.cpython-311.pyc
 ┃ ┃ ┣ 📜Retrival_State.cpython-311.pyc
 ┃ ┃ ┗ 📜Tools.cpython-311.pyc
 ┃ ┣ 📜Agent.py
 ┃ ┣ 📜Graph.py
 ┃ ┣ 📜Retrival_State.py
 ┃ ┗ 📜Tools.py
 ┣ 📂api
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜routes.cpython-311.pyc
 ┃ ┃ ┣ 📜schema.cpython-311.pyc
 ┃ ┃ ┗ 📜services.cpython-311.pyc
 ┃ ┣ 📜routes.py
 ┃ ┣ 📜schema.py
 ┃ ┗ 📜services.py
 ┣ 📂dataIngestionPipelines
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜chroma.cpython-311.pyc
 ┃ ┃ ┣ 📜dataIngestion.cpython-311.pyc
 ┃ ┃ ┣ 📜Images_Ingestion.cpython-311.pyc
 ┃ ┃ ┣ 📜Rank_BM25.cpython-311.pyc
 ┃ ┃ ┣ 📜refine_data.cpython-311.pyc
 ┃ ┃ ┣ 📜SparseIngestion.cpython-311.pyc
 ┃ ┃ ┣ 📜TextIngestion.cpython-311.pyc
 ┃ ┃ ┗ 📜VectorIngestion.cpython-311.pyc
 ┃ ┣ 📜Images_Ingestion.py
 ┃ ┣ 📜Rank_BM25.py
 ┃ ┣ 📜SparseIngestion.py
 ┃ ┗ 📜VectorIngestion.py
 ┣ 📂DB
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜postgres.cpython-311.pyc
 ┃ ┃ ┣ 📜redis.cpython-311.pyc
 ┃ ┃ ┣ 📜SparseDataBase.cpython-311.pyc
 ┃ ┃ ┗ 📜VectorDataBase.cpython-311.pyc
 ┃ ┣ 📜postgres.py
 ┃ ┣ 📜redis.py
 ┃ ┣ 📜SparseDataBase.py
 ┃ ┗ 📜VectorDataBase.py
 ┣ 📂email
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜authenticate_gmail_api.cpython-311.pyc
 ┃ ┃ ┣ 📜email_read.cpython-311.pyc
 ┃ ┃ ┗ 📜email_Send.cpython-311.pyc
 ┃ ┣ 📜authenticate_gmail_api.py
 ┃ ┣ 📜email_read.py
 ┃ ┗ 📜email_Send.py
 ┣ 📂Help
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┗ 📜refine_data.cpython-311.pyc
 ┃ ┗ 📜refine_data.py
 ┣ 📂RetrivalPipelines
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜ImageRetriver.cpython-311.pyc
 ┃ ┃ ┣ 📜Model.cpython-311.pyc
 ┃ ┃ ┣ 📜Prompt.cpython-311.pyc
 ┃ ┃ ┣ 📜Retirval.cpython-311.pyc
 ┃ ┃ ┣ 📜Retrival.cpython-311.pyc
 ┃ ┃ ┣ 📜RRF.cpython-311.pyc
 ┃ ┃ ┣ 📜SparseRetrival.cpython-311.pyc
 ┃ ┃ ┣ 📜System_Prompt_Generation.cpython-311.pyc
 ┃ ┃ ┗ 📜vectorRetrival.cpython-311.pyc
 ┃ ┣ 📜ImageRetriver.py
 ┃ ┣ 📜Prompt.py
 ┃ ┣ 📜Retrival.py
 ┃ ┣ 📜RRF.py
 ┃ ┣ 📜SparseRetrival.py
 ┃ ┣ 📜System_Prompt_Generation.py
 ┃ ┗ 📜vectorRetrival.py
 ┣ 📂taskscheduling
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┣ 📜celery.cpython-311.pyc
 ┃ ┃ ┣ 📜handle_task.cpython-311.pyc
 ┃ ┃ ┣ 📜schedular.cpython-311.pyc
 ┃ ┃ ┣ 📜schema.cpython-311.pyc
 ┃ ┃ ┣ 📜services.cpython-311.pyc
 ┃ ┃ ┣ 📜task.cpython-311.pyc
 ┃ ┃ ┗ 📜tasks.cpython-311.pyc
 ┃ ┣ 📜celery.py
 ┃ ┣ 📜handle_task.py
 ┃ ┣ 📜schedular.py
 ┃ ┣ 📜schema.py
 ┃ ┣ 📜services.py
 ┃ ┗ 📜tasks.py
 ┣ 📂__pycache__
 ┃ ┣ 📜config.cpython-311.pyc
 ┃ ┣ 📜test.cpython-311.pyc
 ┃ ┗ 📜__init__.cpython-311.pyc
 ┣ 📜config.py
 ┗ 📜__init__.py
 ```