import hashlib
import json
import logging
from pathlib import PurePosixPath

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas import DocumentMetadata
from app.services.document_parser import extract_text


logger = logging.getLogger("knowbase")


SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".pdf",
    ".docx",
}


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    async def index_documents(
        self,
        files: list[UploadFile],
        metadata: str,
    ) -> list[DocumentMetadata]:
        metadata_list = json.loads(metadata)

        if len(metadata_list) != len(files):
            raise ValueError(
                "The number of files does not match the metadata."
            )

        documents: list[DocumentMetadata] = []

        logger.info(
            "Received %d files",
            len(files),
        )

        for index, file in enumerate(files):
            try:
                document_metadata = metadata_list[index]

                document = await self._index_document(
                    file=file,
                    metadata=document_metadata,
                )

                if document is not None:
                    documents.append(document)

            finally:
                await file.close()

        self.db.commit()

        return documents

    async def _index_document(
        self,
        file: UploadFile,
        metadata: dict,
    ) -> DocumentMetadata | None:
        filename = file.filename or "unknown"
        extension = PurePosixPath(filename).suffix.lower()

        logger.info(
            "Processing: %s",
            filename,
        )

        if extension not in SUPPORTED_EXTENSIONS:
            logger.warning(
                "Unsupported file: %s",
                filename,
            )

            return None

        content = await file.read()

        text = extract_text(
            filename,
            content,
        )

        content_hash = hashlib.sha256(
            content
        ).hexdigest()

        existing_document = self.db.scalar(
            select(Document).where(
                Document.path == metadata["path"]
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

            logger.info(
                "Updated document: %s",
                filename,
            )

        else:
            document = Document(
                name=filename,
                path=metadata["path"],
                extension=extension,
                content_type=file.content_type,
                size=len(content),
                content=text,
                content_hash=content_hash,
            )

            self.db.add(document)

            logger.info(
                "Created document: %s",
                filename,
            )

        self.db.flush()

        return DocumentMetadata(
            id=document.id,
            name=document.name,
            path=document.path,
            size=document.size,
            content_type=document.content_type,
            extension=document.extension,
            text_length=len(document.content),
            text_preview=document.content[:500],
        )