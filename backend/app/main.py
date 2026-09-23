from typing import Annotated
import json
from pathlib import PurePosixPath

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel

app = FastAPI()


SUPPORTED_EXTENSIONS = {
    '.md',
    '.txt',
    '.pdf',
    '.doc',
    '.docx',
}

class FileMetadata(BaseModel):
    name: str
    path: str
    size: int
    content_type: str | None
    extension: str


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

        documents.append(
            FileMetadata(
                name=filename,
                path=file_metadata['path'],
                size=len(content),
                content_type=file.content_type,
                extension=extension,
            )
        )

        await file.close()

    return FilesResponse(
        total=len(documents),
        files=documents,
    )