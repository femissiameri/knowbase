from app.schemas import RAGContextResponse
from app.services.llm_service import LLMService
from app.services.rag_context_service import RAGContextService


class RAGAnswerService:
    def __init__(self, db):
        self.context_service = RAGContextService(db)
        self.llm = LLMService()

    def answer(self, query: str) -> tuple[str, RAGContextResponse]:
        rag_context = self.context_service.build_context(
            query=query,
            limit=5,
            max_characters=8000,
        )

        if not rag_context.sources:
            return (
                "I couldn't find relevant information in your knowledge base.",
                rag_context,
            )

        prompt = self._build_prompt(
            query=query,
            context=rag_context.context,
        )

        answer = self.llm.generate(prompt)

        return answer, rag_context

    @staticmethod
    def _build_prompt(query: str, context: str) -> str:
        return f"""
You are KnowBase, a private AI knowledge assistant.

Answer the user's question using only the information provided
in the context below.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- If the context does not contain enough information, say so.
- Keep the answer clear and concise.
- Cite the relevant sources using [SOURCE N].
- Only cite sources that actually support the statement.

Context:
{context}

User question:
{query}

Answer:
""".strip()