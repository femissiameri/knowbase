from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    id: int
    name: str
    path: str
    size: int
    content_type: str | None
    extension: str
    text_length: int
    text_preview: str
    chunk_count: int


class DocumentsResponse(BaseModel):
    total: int
    documents: list[DocumentMetadata]


class SyncResult(BaseModel):
    created: int
    updated: int
    unchanged: int
    deleted: int
    documents: list[DocumentMetadata]


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_name: str
    document_path: str
    chunk_index: int
    content: str
    page_number: int | None
    section: str | None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


class SemanticSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_name: str
    document_path: str
    chunk_index: int
    content: str
    page_number: int | None
    section: str | None
    similarity: float


class SemanticSearchResponse(BaseModel):
    query: str
    total: int
    results: list[SemanticSearchResult]


class HybridSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_name: str
    document_path: str
    chunk_index: int
    content: str
    page_number: int | None
    section: str | None
    similarity: float | None
    matched_by: list[str]


class HybridSearchResponse(BaseModel):
    query: str
    total: int
    results: list[HybridSearchResult]


class RAGSource(BaseModel):
    reference: int
    chunk_id: int
    document_id: int
    document_name: str
    document_path: str
    chunk_index: int
    page_number: int | None
    section: str | None


class RAGContextResponse(BaseModel):
    query: str
    context: str
    sources: list[RAGSource]


class RAGAnswerResponse(BaseModel):
    query: str
    answer: str
    sources: list[RAGSource]