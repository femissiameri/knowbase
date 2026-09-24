import logging

from app.schemas import HybridSearchResult
from app.services.search_service import SearchService
from app.services.semantic_search_service import (
    SemanticSearchService,
)


logger = logging.getLogger("knowbase")


RRF_K = 60
KEYWORD_LIMIT = 30
SEMANTIC_LIMIT = 30

# This is deliberately conservative for the MVP.
# We will tune this after testing on real documents.
MIN_SEMANTIC_SIMILARITY = 0.20


class HybridSearchService:
    def __init__(self, db):
        self.db = db

        self.keyword_search = SearchService(db)
        self.semantic_search = SemanticSearchService(db)

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[HybridSearchResult]:
        keyword_results = (
            self.keyword_search.search(
                query=query,
                limit=KEYWORD_LIMIT,
            )
        )

        semantic_results = (
            self.semantic_search.search(
                query=query,
                limit=SEMANTIC_LIMIT,
            )
        )

        # Remove weak semantic-only results.
        semantic_results = [
            result
            for result in semantic_results
            if result.similarity
            >= MIN_SEMANTIC_SIMILARITY
        ]

        scores: dict[int, float] = {}

        results_by_chunk: dict[
            int,
            HybridSearchResult,
        ] = {}

        # -------------------------------
        # Keyword ranking
        # -------------------------------

        for rank, result in enumerate(
            keyword_results,
            start=1,
        ):
            chunk_id = result.chunk_id

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + 1.0 / (RRF_K + rank)
            )

            results_by_chunk[chunk_id] = (
                HybridSearchResult(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    document_name=result.document_name,
                    document_path=result.document_path,
                    chunk_index=result.chunk_index,
                    content=result.content,
                    similarity=None,
                    matched_by=["keyword"],
                )
            )

        # -------------------------------
        # Semantic ranking
        # -------------------------------

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = result.chunk_id

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + 1.0 / (RRF_K + rank)
            )

            if chunk_id in results_by_chunk:
                results_by_chunk[
                    chunk_id
                ].similarity = result.similarity

                if "semantic" not in (
                    results_by_chunk[
                        chunk_id
                    ].matched_by
                ):
                    results_by_chunk[
                        chunk_id
                    ].matched_by.append(
                        "semantic"
                    )

            else:
                results_by_chunk[chunk_id] = (
                    HybridSearchResult(
                        chunk_id=result.chunk_id,
                        document_id=result.document_id,
                        document_name=result.document_name,
                        document_path=result.document_path,
                        chunk_index=result.chunk_index,
                        content=result.content,
                        similarity=result.similarity,
                        matched_by=["semantic"],
                    )
                )

        ranked = sorted(
            results_by_chunk.values(),
            key=lambda result: scores[
                result.chunk_id
            ],
            reverse=True,
        )

        results = ranked[:limit]

        logger.info(
            "Hybrid search '%s' returned %d results",
            query,
            len(results),
        )

        return results