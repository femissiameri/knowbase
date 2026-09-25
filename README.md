# KnowBase

> Your private AI knowledge base, running locally.

KnowBase is an open-source, local-first application that lets you ask questions about your own documents and get answers grounded in your files.

The goal is simple:

**Select your knowledge → index it locally → search it → ask questions → get answers with sources.**

## Why KnowBase?

Important information is often spread across:

- Documentation
- PDFs
- Markdown files
- Text files
- Project files
- Internal knowledge

Searching through everything manually is slow, while sending private documents to a cloud service may not be appropriate.

KnowBase is designed around a local-first workflow: documents are indexed and stored locally, retrieval happens locally, and AI answers can be generated with a local LLM.

## Current Features

- Local folder selection from the web interface
- Document synchronization with created, updated, unchanged and deleted detection
- PDF, DOCX, Markdown and TXT parsing
- Source-aware chunking with page and section metadata
- SQLite persistence
- Full-text search with SQLite FTS5
- Local semantic search with embeddings
- Hybrid retrieval combining keyword and semantic search
- Reciprocal Rank Fusion (RRF) for hybrid ranking
- Phrase-aware RAG reranking
- Grounded question answering using retrieved document context
- Source references with document, page and chunk metadata
- Local LLM integration through Ollama
- Vue-based search and document management interface
- Responsive UI with reusable Vue components and composables

## How It Works

```text
Local folder
    ↓
File discovery
    ↓
Document parsing
    ↓
Metadata + content
    ↓
Chunking
    ↓
SQLite + FTS5 + embeddings
    ↓
Hybrid retrieval
    ↓
RAG context
    ↓
Local LLM
    ↓
Answer + sources
```

## Architecture

KnowBase is organized as a monorepo:

```text
knowbase/
├── frontend/            # Vue 3 + TypeScript
├── backend/             # FastAPI + Python
├── docs/                # Documentation
├── .github/             # GitHub configuration
├── LICENSE
├── README.md
└── .gitignore
```

### Frontend structure

The frontend is split into reusable views, components, composables, types and utilities:

```text
frontend/src/
├── components/
│   ├── common/
│   ├── documents/
│   ├── layout/
│   └── search/
├── composables/
├── types/
├── utils/
├── views/
├── App.vue
└── main.ts
```

### Backend structure

```text
backend/app/
├── services/
│   ├── document_parser.py
│   ├── document_service.py
│   ├── embedding_service.py
│   ├── hybrid_search_service.py
│   ├── llm_service.py
│   ├── rag_answer_service.py
│   ├── rag_context_service.py
│   └── ...
├── database.py
├── models.py
├── schemas.py
└── main.py
```

## Tech Stack

### Frontend

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- pnpm

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- uv

### Document Processing

- PyMuPDF for PDF extraction
- python-docx for DOCX extraction
- Markdown and TXT parsing

### Search

- SQLite FTS5 for keyword search
- Sentence Transformers for semantic embeddings
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Hybrid retrieval with Reciprocal Rank Fusion

### AI

- Ollama
- Qwen 2.5 14B for local answer generation

The AI pipeline is designed so that retrieved document context is provided to the local model, allowing answers to be grounded in the user's indexed knowledge.

## Supported Documents

The current supported formats are:

| Format | Support |
|---|---|
| `.pdf` | Yes |
| `.docx` | Yes |
| `.md` | Yes |
| `.txt` | Yes |
| `.doc` | Not supported yet |

## Local Data

KnowBase keeps its application data locally.

The development SQLite database is stored at:

```text
backend/data/knowbase.db
```

This database is intentionally excluded from Git.

Embeddings and document chunks are persisted locally so the indexed knowledge can survive backend restarts.

## Local AI Setup

KnowBase uses Ollama for local LLM inference.

Make sure Ollama is installed and running, then pull the model:

```bash
ollama pull qwen2.5:14b
```

Verify the model:

```bash
ollama list
```

You can also test it directly:

```bash
ollama run qwen2.5:14b
```

The backend connects to Ollama at:

```text
http://localhost:11434
```

The model and timeout can be configured with environment variables:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_TIMEOUT=300
```

## Development

### Prerequisites

Make sure the following are installed:

- Node.js
- pnpm
- Python 3.12+
- uv
- Ollama

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Backend

```bash
cd backend
uv sync
uv run fastapi dev
```

The FastAPI application will be available at:

```text
http://localhost:8000
```

The API documentation is available at:

```text
http://localhost:8000/docs
```

## API Overview

The backend currently exposes endpoints for:

```text
GET  /api/health
GET  /api/documents
POST /api/documents/sync

GET  /api/search
GET  /api/search/semantic
GET  /api/search/hybrid

GET  /api/rag/context
GET  /api/rag/answer
```

The search endpoints expose retrieval directly, while the RAG endpoints build context and generate grounded answers.

## Privacy Model

KnowBase is built with a local-first approach.

The core workflow is:

```text
Your files
   ↓
Your machine
   ↓
Local database
   ↓
Local retrieval
   ↓
Local LLM
```

No external AI provider is required for the core RAG workflow.

Third-party integrations may be added in the future as optional features.

## Project Status

KnowBase is currently in early development.

The first end-to-end milestone is now functional:

```text
Folder
  ↓
File discovery
  ↓
Parsing
  ↓
Metadata
  ↓
Chunking
  ↓
Keyword + semantic search
  ↓
Hybrid retrieval
  ↓
RAG context
  ↓
Local AI answer
  ↓
Sources
```

The project is still being actively refined, especially around retrieval quality, source navigation, UI polish and extensibility.

## Roadmap

Planned improvements include:

- Clickable source citations
- Exact source/document viewer
- Better source highlighting
- Improved retrieval evaluation and reranking
- Additional document formats
- Knowledge-base/workspace isolation
- Background indexing
- Streaming LLM responses
- More local embedding options
- Developer-friendly CLI
- Optional external service integrations
- Automated tests across indexing, retrieval and RAG

## Contributing

Contributions, ideas and feedback are welcome.

Before submitting a pull request:

1. Check the existing issues and documentation.
2. Keep changes focused.
3. Add or update tests when appropriate.
4. Follow the existing project structure and coding conventions.

## License

KnowBase is released under the [MIT License](LICENSE).
