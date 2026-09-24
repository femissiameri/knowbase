import logging

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, ChunkEmbedding, Document
from app.schemas import SemanticSearchResult
from app.services.embedding_service import embed_text
from app.services.vector_storage import deserialize_vector


logger = logging.getLogger("knowbase")


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SemanticSearchResult]:
        query = query.strip()

        if not query:
            return []

        query_vector = np.asarray(
            embed_text(query),
            dtype=np.float32,
        )

        rows = self.db.execute(
            select(
                Chunk,
                ChunkEmbedding,
                Document,
            )
            .join(
                ChunkEmbedding,
                ChunkEmbedding.chunk_id == Chunk.id,
            )
            .join(
                Document,
                Document.id == Chunk.document_id,
            )
            .where(
                ChunkEmbedding.model == MODEL_NAME
            )
        ).all()

        scored_results: list[tuple[
            float,
            SemanticSearchResult,
        ]] = []

        for chunk, embedding, document in rows:
            chunk_vector = deserialize_vector(
                embedding.vector
            )

            similarity = float(
                np.dot(
                    query_vector,
                    chunk_vector,
                )
            )

            scored_results.append(
                (
                    similarity,
                    SemanticSearchResult(
                        chunk_id=chunk.id,
                        document_id=document.id,
                        document_name=document.name,
                        document_path=document.path,
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        page_number=chunk.page_number,
                        section=chunk.section,
                        similarity=similarity,
                    ),
                )
            )

        scored_results.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        results = [
            result
            for _, result in scored_results[:limit]
        ]

        logger.info(
            "Semantic search '%s' returned %d results",
            query,
            len(results),
        )

        return results