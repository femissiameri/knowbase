import hashlib
import json
import logging
from pathlib import PurePosixPath

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas import DocumentMetadata, SyncResult
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

    async def sync_documents(
        self,
        files: list[UploadFile],
        metadata: str,
        folder_name: str,
    ) -> SyncResult:
        metadata_list = json.loads(metadata)

        if len(metadata_list) != len(files):
            raise ValueError(
                "The number of files does not match the metadata."
            )

        created = 0
        updated = 0
        unchanged = 0

        current_paths: set[str] = set()

        for index, file in enumerate(files):
            document_metadata = metadata_list[index]

            path = document_metadata["path"]

            current_paths.add(path)

            result = await self._sync_document(
                file=file,
                metadata=document_metadata,
            )

            if result == "created":
                created += 1

            elif result == "updated":
                updated += 1

            elif result == "unchanged":
                unchanged += 1

        deleted = self._delete_missing_documents(
            folder_name=folder_name,
            current_paths=current_paths,
        )

        self.db.commit()

        documents = self.list_documents(
            folder_name=folder_name,
        )

        return SyncResult(
            created=created,
            updated=updated,
            unchanged=unchanged,
            deleted=deleted,
            documents=documents,
        )

    async def _sync_document(
        self,
        file: UploadFile,
        metadata: dict,
    ) -> str:
        filename = file.filename or "unknown"

        extension = PurePosixPath(
            filename
        ).suffix.lower()

        logger.info(
            "Processing: %s",
            filename,
        )

        if extension not in SUPPORTED_EXTENSIONS:
            logger.warning(
                "Unsupported file: %s",
                filename,
            )

            return "unchanged"

        content = await file.read()

        content_hash = hashlib.sha256(
            content
        ).hexdigest()

        existing_document = self.db.scalar(
            select(Document).where(
                Document.path == metadata["path"]
            )
        )

        # File exists and content has not changed.
        if (
            existing_document
            and existing_document.content_hash
            == content_hash
        ):
            logger.info(
                "Unchanged: %s",
                filename,
            )

            return "unchanged"

        text = extract_text(
            filename,
            content,
        )

        if existing_document:
            existing_document.name = filename
            existing_document.extension = extension
            existing_document.content_type = file.content_type
            existing_document.size = len(content)
            existing_document.content = text
            existing_document.content_hash = content_hash

            logger.info(
                "Updated: %s",
                filename,
            )

            return "updated"

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
            "Created: %s",
            filename,
        )

        return "created"

    def _delete_missing_documents(
        self,
        folder_name: str,
        current_paths: set[str],
    ) -> int:
        prefix = f"{folder_name}/"

        stored_documents = self.db.scalars(
            select(Document).where(
                Document.path.like(f"{prefix}%")
            )
        ).all()

        deleted = 0

        for document in stored_documents:
            if document.path not in current_paths:
                logger.info(
                    "Deleted: %s",
                    document.path,
                )

                self.db.delete(document)
                deleted += 1

        return deleted

    def list_documents(
        self,
        folder_name: str | None = None,
    ) -> list[DocumentMetadata]:
        query = select(Document).order_by(
            Document.updated_at.desc()
        )

        if folder_name:
            query = query.where(
                Document.path.like(
                    f"{folder_name}/%"
                )
            )

        documents = self.db.scalars(
            query
        ).all()

        return [
            DocumentMetadata(
                id=document.id,
                name=document.name,
                path=document.path,
                size=document.size,
                content_type=document.content_type,
                extension=document.extension,
                text_length=len(document.content),
                text_preview=document.content[:500],
            )
            for document in documents
        ]