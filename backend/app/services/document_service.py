import hashlib
import json
import logging
from pathlib import PurePosixPath

from fastapi import UploadFile
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models import (
    Chunk,
    ChunkEmbedding,
    Document,
)
from app.services.embedding_service import (
    EmbeddingService,
)
from app.schemas import DocumentMetadata, SyncResult
from app.services.document_parser import (
    extract_pages,
)
from app.services.chunker import (
    chunk_pages,
)
from app.services.chunker import chunk_text


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
        self.embedding_service = EmbeddingService(db)

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
            embedding_count = (
                self.embedding_service
                .ensure_document_embeddings(
                    existing_document.id
                )
            )

            logger.info(
                "Unchanged: %s",
                filename,
            )

            logger.info(
                "Verified embeddings for %d chunks of %s",
                embedding_count,
                filename,
            )

            return "unchanged"

        pages = extract_pages(
            filename,
            content,
        )

        text = "\n\n".join(
            page.text
            for page in pages
        )

        if existing_document:
            existing_document.name = filename
            existing_document.extension = extension
            existing_document.content_type = file.content_type
            existing_document.size = len(content)
            existing_document.content = text
            existing_document.content_hash = content_hash

            document = existing_document

            self.db.flush()

            self._replace_chunks(
                document,
                pages,
            )

            embedding_count = (
                self.embedding_service
                .ensure_document_embeddings(
                    document.id
                )
            )

            logger.info(
                "Updated: %s",
                filename,
            )

            logger.info(
                "Generated embeddings for %d chunks of %s",
                embedding_count,
                document.name,
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

        self.db.flush()

        self._replace_chunks(
            document,
            pages,
        )

        embedding_count = (
            self.embedding_service
            .ensure_document_embeddings(
                document.id
            )
        )

        logger.info(
            "Created: %s",
            filename,
        )

        logger.info(
            "Generated embeddings for %d chunks of %s",
            embedding_count,
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

                chunk_ids = select(
                    Chunk.id
                ).where(
                    Chunk.document_id == document.id
                )

                self.db.execute(
                    delete(ChunkEmbedding).where(
                        ChunkEmbedding.chunk_id.in_(
                            chunk_ids
                        )
                    )
                )

                self.db.execute(
                    delete(Chunk).where(
                        Chunk.document_id == document.id
                    )
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
                chunk_count=self._get_chunk_count(
                    document.id
                ),
            )
            for document in documents
        ]

    def _replace_chunks(
        self,
        document: Document,
        pages,
    ) -> int:
        chunk_ids = select(
            Chunk.id
        ).where(
            Chunk.document_id == document.id
        )

        # Remove embeddings belonging to the old chunks.
        self.db.execute(
            delete(ChunkEmbedding).where(
                ChunkEmbedding.chunk_id.in_(
                    chunk_ids
                )
            )
        )

        # Remove the old chunks.
        self.db.execute(
            delete(Chunk).where(
                Chunk.document_id == document.id
            )
        )

        chunks = chunk_pages(
            pages
        )

        for index, (
            content,
            start_position,
            end_position,
            page_number,
            section,
        ) in enumerate(chunks):
            self.db.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    start_position=start_position,
                    end_position=end_position,
                    page_number=page_number,
                    section=section,
                )
            )

        # We need chunk IDs before creating embeddings.
        self.db.flush()

        logger.info(
            "Created %d chunks for %s",
            len(chunks),
            document.name,
        )

        return len(chunks)

    def _get_chunk_count(
        self,
        document_id: int,
    ) -> int:
        return len(
            self.db.scalars(
                select(Chunk).where(
                    Chunk.document_id == document_id
                )
            ).all()
        )