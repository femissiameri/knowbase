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


class DocumentsResponse(BaseModel):
    total: int
    documents: list[DocumentMetadata]