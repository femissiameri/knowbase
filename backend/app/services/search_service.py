import logging
import re

from sqlalchemy import text
from sqlalchemy.orm import Session

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
        fts_query = self._build_fts_query(query)

        if not fts_query:
            return []

        statement = text(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id AS document_id,
                d.name AS document_name,
                d.path AS document_path,
                c.chunk_index AS chunk_index,
                c.content AS content
            FROM chunks_fts AS f
            JOIN chunks AS c
                ON c.id = f.rowid
            JOIN documents AS d
                ON d.id = c.document_id
            WHERE chunks_fts MATCH :query
            ORDER BY bm25(chunks_fts)
            LIMIT :limit
            """
        )

        rows = self.db.execute(
            statement,
            {
                "query": fts_query,
                "limit": limit,
            },
        ).mappings().all()

        logger.info(
            "FTS search '%s' returned %d results",
            query,
            len(rows),
        )

        return [
            SearchResult(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                document_name=row["document_name"],
                document_path=row["document_path"],
                chunk_index=row["chunk_index"],
                content=row["content"],
            )
            for row in rows
        ]

    @staticmethod
    def _build_fts_query(query: str) -> str:
        terms = re.findall(
            r"\w+",
            query,
            flags=re.UNICODE,
        )

        if not terms:
            return ""

        return " AND ".join(
            f'"{term}"'
            for term in terms
        )