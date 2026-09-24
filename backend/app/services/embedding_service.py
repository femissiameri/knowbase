from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, ChunkEmbedding
from app.services.vector_storage import serialize_vector


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


class EmbeddingService:
    def __init__(self, db: Session):
        self.db = db

    def ensure_document_embeddings(
        self,
        document_id: int,
    ) -> int:
        chunks = self.db.scalars(
            select(Chunk)
            .where(
                Chunk.document_id == document_id
            )
            .order_by(Chunk.chunk_index)
        ).all()

        if not chunks:
            return 0

        chunk_ids = [
            chunk.id
            for chunk in chunks
        ]

        existing_embeddings = self.db.scalars(
            select(ChunkEmbedding)
            .where(
                ChunkEmbedding.chunk_id.in_(
                    chunk_ids
                )
            )
        ).all()

        existing_chunk_ids = {
            embedding.chunk_id
            for embedding in existing_embeddings
            if embedding.model == MODEL_NAME
        }

        missing_chunks = [
            chunk
            for chunk in chunks
            if chunk.id not in existing_chunk_ids
        ]

        if not missing_chunks:
            return len(existing_embeddings)

        model = get_model()

        texts = [
            chunk.content
            for chunk in missing_chunks
        ]

        vectors = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        for chunk, vector in zip(
            missing_chunks,
            vectors,
        ):
            embedding = ChunkEmbedding(
                chunk_id=chunk.id,
                model=MODEL_NAME,
                dimensions=len(vector),
                vector=serialize_vector(
                    vector.tolist()
                ),
            )

            self.db.add(embedding)

        self.db.flush()

        return len(chunks)