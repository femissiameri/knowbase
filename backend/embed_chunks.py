from sqlalchemy import select

from app.database import SessionLocal
from app.models import Chunk, ChunkEmbedding
from app.services.embedding_service import embed_text
from app.services.vector_storage import serialize_vector


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def main() -> None:
    db = SessionLocal()

    try:
        chunks = db.scalars(
            select(Chunk).order_by(Chunk.id)
        ).all()

        print(f"Found {len(chunks)} chunks.")

        for chunk in chunks:
            existing = db.scalar(
                select(ChunkEmbedding).where(
                    ChunkEmbedding.chunk_id == chunk.id
                )
            )

            if existing:
                print(
                    f"Skipping chunk {chunk.id}: "
                    "embedding already exists."
                )
                continue

            print(
                f"Embedding chunk {chunk.id}..."
            )

            vector = embed_text(chunk.content)

            embedding = ChunkEmbedding(
                chunk_id=chunk.id,
                model=MODEL_NAME,
                dimensions=len(vector),
                vector=serialize_vector(vector),
            )

            db.add(embedding)

        db.commit()

        print("Embedding generation complete.")

    finally:
        db.close()


if __name__ == "__main__":
    main()