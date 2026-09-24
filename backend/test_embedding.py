from app.services.embedding_service import (
    embed_text,
)


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:
    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    magnitude_a = sum(
        x * x
        for x in a
    ) ** 0.5

    magnitude_b = sum(
        y * y
        for y in b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


text_a = (
    "What are the objectives of the training?"
)

text_b = (
    "Quels sont les objectifs de la formation ?"
)

text_c = (
    "The weather is beautiful today."
)


embedding_a = embed_text(text_a)
embedding_b = embed_text(text_b)
embedding_c = embed_text(text_c)


print(
    "English ↔ French:",
    cosine_similarity(
        embedding_a,
        embedding_b,
    ),
)

print(
    "English ↔ Weather:",
    cosine_similarity(
        embedding_a,
        embedding_c,
    ),
)