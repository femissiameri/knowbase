import logging

from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database import (
    Base,
    engine,
    get_db,
    initialize_fts,
)
from app.schemas import (
    DocumentsResponse,
    HybridSearchResponse,
    RAGContextResponse,
    SearchResponse,
    SemanticSearchResponse,
    SyncResult,
)
from app.services.rag_context_service import (
    RAGContextService,
)
from app.services.hybrid_search_service import (
    HybridSearchService,
)
from app.services.semantic_search_service import (
    SemanticSearchService,
)
from app.services.search_service import SearchService
from app.services.document_service import DocumentService


logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger("knowbase")


app = FastAPI(
    title="KnowBase API",
    version="0.1.0",
)


Base.metadata.create_all(bind=engine)
initialize_fts()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "knowbase-api",
    }


@app.get(
    "/api/documents",
    response_model=DocumentsResponse,
)
async def list_documents(
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    documents = service.list_documents()

    return DocumentsResponse(
        total=len(documents),
        documents=documents,
    )


@app.post(
    "/api/documents/sync",
    response_model=SyncResult,
)
async def sync_documents(
    files: Annotated[list[UploadFile], File()],
    metadata: Annotated[str, Form()],
    folder_name: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    return await service.sync_documents(
        files=files,
        metadata=metadata,
        folder_name=folder_name,
    )


@app.get(
    "/api/search",
    response_model=SearchResponse,
)
async def search_documents(
    q: str,
    db: Session = Depends(get_db),
):
    service = SearchService(db)

    results = service.search(q)

    return SearchResponse(
        query=q,
        total=len(results),
        results=results,
    )

@app.get(
    "/api/search/semantic",
    response_model=SemanticSearchResponse,
)
async def semantic_search(
    q: str,
    db: Session = Depends(get_db),
):
    service = SemanticSearchService(db)

    results = service.search(q)

    return SemanticSearchResponse(
        query=q,
        total=len(results),
        results=results,
    )


@app.get(
    "/api/search/hybrid",
    response_model=HybridSearchResponse,
)
async def hybrid_search(
    q: str,
    db: Session = Depends(get_db),
):
    service = HybridSearchService(db)

    results = service.search(q)

    return HybridSearchResponse(
        query=q,
        total=len(results),
        results=results,
    )


@app.get(
    "/api/rag/context",
    response_model=RAGContextResponse,
)
async def build_rag_context(
    q: str,
    db: Session = Depends(get_db),
):
    service = RAGContextService(db)

    return service.build_context(
        query=q,
    )