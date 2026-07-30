# DocuMind – A Conversational AI Document Assistant

## Overview

DocuMind is a Retrieval-Augmented Generation (RAG) based document assistant that allows users to upload PDF documents and interact with them through natural language conversations.

Unlike a traditional PDF chatbot that relies solely on semantic vector search, DocuMind combines multiple retrieval techniques to improve answer quality and reduce irrelevant context. The system supports conversational memory, intelligent document routing, hybrid retrieval, reranking, source citations, and persistent chat history, making it suitable for handling multiple documents while maintaining accurate responses.

The project was built to understand how modern RAG systems work beyond simple embedding search and to explore techniques used in production-grade AI applications.

---

## Features

* Upload and index multiple PDF documents
* Conversational question answering over uploaded documents
* Persistent conversation history
* Automatic query rewriting using conversation context
* Intelligent document routing to reduce unnecessary retrieval
* Hybrid Retrieval (Dense + Keyword Search)
* Reciprocal Rank Fusion (RRF)
* Cross-Encoder Reranking
* Source citations with page references
* FastAPI backend with modular architecture
* SQLite database for chat persistence
* Responsive web interface

---

# System Architecture
<img width="1056" height="708" alt="Rag Project System Architecture" src="https://github.com/user-attachments/assets/f1d76668-7c00-41ee-add2-3d84de84c81a" />


---

# How It Works

### 1. PDF Ingestion

When a PDF is uploaded:

* The document is parsed page by page.
* Each page is divided into overlapping text chunks.
* Sentence Transformer embeddings are generated.
* The chunks, metadata, and embeddings are stored inside ChromaDB.
* BM25 indexes are built for keyword retrieval.

---

### 2. Query Understanding

Before retrieval, the system rewrites the user's latest question using previous conversation history.

For example,

> "What were his responsibilities?"

becomes

> "What were Sanket Kashyap's responsibilities during the Tata Motors internship?"

This significantly improves retrieval quality for follow-up questions.

---

### 3. Document Routing

Instead of searching every uploaded PDF, the system first determines which documents are relevant to the current question.

Example:

Question:

> What is my CGPA?

The router searches only the resume instead of every uploaded document.

This reduces search space and avoids noisy retrieval.

---

### 4. Hybrid Retrieval

Rather than depending on only one retrieval technique, DocuMind combines:

### Dense Retrieval

* Sentence Transformer embeddings
* Semantic similarity search
* ChromaDB vector database

Useful for:

* Conceptual questions
* Paraphrased queries
* Semantic understanding

---

### Sparse Retrieval

* BM25 keyword search

Useful for:

* Exact names
* IDs
* Technical terms
* Acronyms

---

### Reciprocal Rank Fusion (RRF)

The rankings produced by Dense Search and BM25 are merged using Reciprocal Rank Fusion.

This allows both semantic similarity and exact keyword matches to contribute to the final ranking.

---

### Cross-Encoder Reranking

The fused results are passed through a Cross-Encoder model.

Unlike embedding similarity, the Cross-Encoder directly compares:

```
Query + Document Chunk
```

and produces a relevance score.

Only the highest quality chunks are forwarded to the language model.

---

### 5. Response Generation

The retrieved context is injected into the prompt sent to the LLM.

The final response includes:

* Answer
* Source citations
* Page numbers

allowing users to verify every generated answer.

---

# Tech Stack

## Backend

* Python
* FastAPI
* LangChain
* SQLite
* SQLAlchemy
* Pydantic

## AI / Machine Learning

* Sentence Transformers
* ChromaDB
* BM25 (rank-bm25)
* Cross-Encoder Reranker
* Retrieval-Augmented Generation (RAG)

## Frontend

* HTML
* CSS
* JavaScript

---

# Project Structure

```
DocuMind/

│
├── app/
│   ├── api/
│   ├── templates/
│   ├── static/
│   └── main.py
|   └── schemas/
|   └── dependencies.py
│
├── src/
|   ├── data_loader.py
|   ├── text_splitter.py
│   ├── embedding_manager.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── hybrid_search.py
│   ├── reranker.py
│   ├── document_router.py
│   ├── rag_pipeline.py
│   └── llm.py
│
├── database.py
├── models.py
├── crud.py
├── ingest.py
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone <repository-url>
cd DocuMind
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn app.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# Future Improvements

* OCR support for scanned PDFs
* Table-aware document parsing
* Hybrid retrieval weighting
* Metadata-aware retrieval
* Citation highlighting inside PDF
* Docker deployment
* Authentication and user management

---

# Demo

## Application Interface

<img width="1918" height="966" alt="image" src="https://github.com/user-attachments/assets/f6dc3baf-d6a1-4840-8a1e-86684a075fd6" />


---

## Example Conversation
<img width="1918" height="965" alt="image" src="https://github.com/user-attachments/assets/461eb01e-7a17-4458-8c48-058807744c07" />


---

## Retrieval Pipeline

<img width="541" height="884" alt="LLBBReCm4BmZyG--LwtKIhcabwH97r8JAONq0oop0GlOHUibYB_lWfEcFM5cTiSp0wiWbgLlcpGHBmsOBRb-xx4mzoO3OGzdsvY3xw3n26cI9g7ss5cshN7KTeI0aikecmnEB9OD_9q9bIrey5YQast2FshDJCEnygv62C4yFYnc-SdFT5X-1s3prKCGJ_WyGnl2Ct2m4s8-V13YCJ8wnw" src="https://github.com/user-attachments/assets/14f61f4e-f24d-474b-a202-daaf5fdcf1c1" />


---

## Demo GIF

> *(Insert GIF or screen recording here)*

```
Demo GIF Placeholder
```

---

# Author

**Sanket Kashyap**

Built as a personal project to explore modern Retrieval-Augmented Generation (RAG) systems, conversational AI, and hybrid information retrieval techniques.
