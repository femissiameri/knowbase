import re

from app.schemas import RAGContextResponse, RAGSource
from app.services.hybrid_search_service import HybridSearchService


DEFAULT_CONTEXT_LIMIT = 5
DEFAULT_MAX_CONTEXT_CHARACTERS = 8000


class RAGContextService:
    def __init__(self, db):
        self.db = db
        self.hybrid_search = HybridSearchService(db)

    def build_context(
        self,
        query: str,
        limit: int = DEFAULT_CONTEXT_LIMIT,
        max_characters: int = DEFAULT_MAX_CONTEXT_CHARACTERS,
    ) -> RAGContextResponse:

        results = self.hybrid_search.search(
            query=query,
            limit=limit,
        )

        results = self._rerank_results(query, results)

        context_parts = []
        sources = []
        total_characters = 0

        for result in results:
            reference = len(sources) + 1

            source_header = self._format_source_header(
                reference,
                result,
            )

            source_block = (
                f"{source_header}\n"
                f"Content:\n"
                f"{result.content}\n"
            )

            remaining = max_characters - total_characters

            if remaining <= 0:
                break

            if len(source_block) > remaining:
                source_block = source_block[:remaining].rstrip() + "\n"

            context_parts.append(source_block)

            sources.append(
                RAGSource(
                    reference=reference,
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    document_name=result.document_name,
                    document_path=result.document_path,
                    chunk_index=result.chunk_index,
                    page_number=result.page_number,
                    section=result.section,
                )
            )

            total_characters += len(source_block)

        return RAGContextResponse(
            query=query,
            context="\n".join(context_parts),
            sources=sources,
        )

    @staticmethod
    def _rerank_results(query: str, results: list):
        phrases = re.findall(r'"([^"]+)"', query)

        normalized_phrases = [
            phrase.strip().lower()
            for phrase in phrases
            if phrase.strip()
        ]

        if normalized_phrases:
            exact_matches = [
                result
                for result in results
                if all(
                    phrase in result.content.lower()
                    for phrase in normalized_phrases
                )
            ]

            if exact_matches:
                return exact_matches

        def score(result):
            content = result.content.lower()

            exact_phrase_score = sum(
                10
                for phrase in normalized_phrases
                if phrase in content
            )

            semantic_score = (
                result.similarity
                if result.similarity is not None
                else 0
            )

            return exact_phrase_score + semantic_score

        return sorted(results, key=score, reverse=True)


    @staticmethod
    def _format_source_header(reference, result):
        lines = [
            f"[SOURCE {reference}]",
            f"Document: {result.document_name}",
            f"Path: {result.document_path}",
        ]

        if result.page_number is not None:
            lines.append(f"Page: {result.page_number}")

        if result.section:
            lines.append(f"Section: {result.section}")

        lines.append(f"Chunk: {result.chunk_index + 1}")

        return "\n".join(lines)