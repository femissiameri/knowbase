# KnowBase

> Your private AI knowledge base, running locally.

KnowBase is an open-source, local-first application that lets you ask questions about your own documents and get answers grounded in your files.

The goal is simple:

**Select your knowledge → index it locally → ask questions → get answers with sources.**

## Why KnowBase?

Important information is often spread across:

* Documentation
* PDFs
* Markdown files
* Text files
* Project files
* Internal knowledge

Searching through everything manually is slow, while sending private documents to a cloud service may not be appropriate.

KnowBase is designed to keep your knowledge on your machine and make it easier to explore with AI.

## Planned Features

* Local document indexing
* PDF, DOCX, Markdown and TXT support
* Semantic search
* AI-powered question answering
* Source references for answers
* Local AI models
* SQLite-based local storage
* Developer-friendly CLI
* Optional integrations with external services

## Architecture

KnowBase is built as a monorepo:

```text
knowbase/
├── frontend/    # Vue 3 + TypeScript
├── backend/     # FastAPI + Python
├── docs/        # Documentation
├── .github/     # GitHub configuration
├── LICENSE
├── README.md
└── .gitignore
```

## Tech Stack

### Frontend

* Vue 3
* TypeScript
* Vite
* Vue Router
* Pinia

### Backend

* Python
* FastAPI

### Planned AI Stack

* Local LLM
* Local embeddings
* Vector search

The AI and search components will be introduced incrementally as the project evolves.

## Project Status

KnowBase is currently in early development.

The first milestone is to build a reliable local document pipeline:

```text
Folder
  ↓
File discovery
  ↓
Document parsing
  ↓
Metadata
  ↓
Search
  ↓
AI answers
```

## Development

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

## Contributing

Contributions, ideas and feedback are welcome.

Before submitting a pull request, please check the existing issues and documentation.

## License

KnowBase is released under the [MIT License](LICENSE).
