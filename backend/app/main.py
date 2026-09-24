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
    SearchResponse,
    SyncResult,
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