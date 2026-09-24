from app.services.chunker import chunk_text


text = """
KnowBase is a private AI knowledge base.

It allows users to index documents locally.

Documents are converted into text and then divided into smaller chunks.

Those chunks will later be used for semantic search.
"""


chunks = chunk_text(
    text,
    chunk_size=50,
    overlap=20,
)


for index, (content, start, end) in enumerate(chunks):
    print("=" * 60)
    print("Chunk:", index)
    print("Position:", start, "→", end)
    print(content)