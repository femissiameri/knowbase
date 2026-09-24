import hashlib
import json
from pathlib import PurePosixPath
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Document

from app.services.document_parser import extract_text

app = FastAPI(
    title="KnowBase API",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)


SUPPORTED_EXTENSIONS = {
    '.md',
    '.txt',
    '.pdf',
    '.docx',
}

class FileMetadata(BaseModel):
    id: int
    name: str
    path: str
    size: int
    content_type: str | None
    extension: str
    text_length: int
    text_preview: str


class FilesResponse(BaseModel):
    total: int
    files: list[FileMetadata]


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "knowbase-api",
    }


@app.post("/api/files", response_model=FilesResponse)
async def upload_files(
    files: Annotated[list[UploadFile], File()],
    metadata: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    metadata_list = json.loads(metadata)

    documents: list[FileMetadata] = []

    for index, file in enumerate(files):
        file_metadata = metadata_list[index]
        filename = file.filename or 'unknown'

        extension = PurePosixPath(filename).suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            continue

        
        # Read the file so we verify the upload acctually reached
        # the backend. We intentionally do not persist it yet.
        content = await file.read()

        text = extract_text(filename, content)

        content_hash = hashlib.sha256(
            content
        ).hexdigest()

        existing_document = db.scalar(
            select(Document).where(
                Document.path == file_metadata["path"]
            )
        )

        if existing_document:
            existing_document.name = filename
            existing_document.extension = extension
            existing_document.content_type = file.content_type
            existing_document.size = len(content)
            existing_document.content = text
            existing_document.content_hash = content_hash

            document = existing_document


        else:
            document = Document(
                name=filename,
                path=file_metadata["path"],
                extension=extension,
                content_type=file.content_type,
                size=len(content),
                content=text,
                content_hash=content_hash,
            )

            db.add(document)


        db.flush()

        documents.append(
            FileMetadata(
                id=document.id,
                name=document.name,
                path=document.path,
                size=document.size,
                content_type=document.content_type,
                extension=document.extension,
                text_length=len(document.content),
                text_preview=document.content[:500],
            )
        )

        await file.close()

    db.commit()

    return FilesResponse(
        total=len(documents),
        files=documents,
    )