
# Palm Mind AI — Conversational RAG Backend

A modular FastAPI backend for document ingestion, retrieval-augmented
question answering, Redis-backed conversation memory, and interview
booking.

## Features

- PDF and TXT document uploads
- Fixed-size and sentence-aware text chunking
- Semantic embeddings using Sentence Transformers
- Qdrant vector storage and similarity search
- PostgreSQL document metadata and interview bookings
- Groq-powered conversational RAG
- Redis-backed multi-turn chat history
- Interview booking through a conversational workflow
- Interactive API documentation with FastAPI

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL and SQLAlchemy
- Redis
- Qdrant
- Sentence Transformers
- Groq API

## Prerequisites

- Python 3.11 or newer
- Docker Desktop with Docker Compose
- A Groq API key

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and set your own Groq API key.

### 4. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, and Qdrant.

### 5. Initialize database tables

```bash
python -m app.db.init_db
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.

## Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic application status |
| GET | `/health` | Application health check |
| POST | `/api/v1/documents` | Upload and process a document |
| POST | `/api/v1/chat` | Ask questions or continue a conversation |
| POST | `/api/v1/bookings` | Create an interview booking directly |

The conversational booking workflow is also available through
the chat endpoint.

## Running Tests

```bash
python -m pytest -v
```

Some tests may require local services or a valid Groq API key.

## Architecture

1. FastAPI receives document uploads.
2. PyMuPDF or UTF-8 text decoding extracts content.
3. A configurable chunking strategy splits the text.
4. Sentence Transformers creates embeddings.
5. Qdrant stores vectors and chunk payloads.
6. PostgreSQL stores document metadata and bookings.
7. Redis stores conversational history and booking drafts.
8. The LLM answers questions using retrieved document context.
