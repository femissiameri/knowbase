import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.schemas import SearchResult


logger = logging.getLogger("knowbase")


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[SearchResult]:
        query = query.strip()

        if not query:
            return []

        pattern = f"%{query}%"

        statement = (
            select(Chunk, Document)
            .join(
                Document,
                Chunk.document_id == Document.id,
            )
            .where(
                Chunk.content.ilike(pattern)
            )
            .order_by(
                Document.name,
                Chunk.chunk_index,
            )
            .limit(limit)
        )

        rows = self.db.execute(statement).all()

        logger.info(
            "Search '%s' returned %d results",
            query,
            len(rows),
        )

        return [
            SearchResult(
                chunk_id=chunk.id,
                document_id=document.id,
                document_name=document.name,
                document_path=document.path,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
            )
            for chunk, document in rows
        ]