import re


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 200


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    ).strip()


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size."
        )

    text = normalize_text(text)

    chunks: list[tuple[str, int, int]] = []

    start = 0
    text_length = len(text)

    while start < text_length:
        target_end = min(
            start + chunk_size,
            text_length,
        )

        end = target_end

        if target_end < text_length:
            boundary = find_boundary(
                text=text,
                start=start,
                target_end=target_end,
            )

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            actual_start = text.find(
                chunk,
                start,
                end,
            )

            actual_start = (
                start
                if actual_start == -1
                else actual_start
            )

            actual_end = actual_start + len(chunk)

            chunks.append(
                (
                    chunk,
                    actual_start,
                    actual_end,
                )
            )

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def find_boundary(
    text: str,
    start: int,
    target_end: int,
) -> int:
    search_start = start + 1

    paragraph_break = text.rfind(
        "\n\n",
        search_start,
        target_end,
    )

    if paragraph_break != -1:
        return paragraph_break

    line_break = text.rfind(
        "\n",
        search_start,
        target_end,
    )

    if line_break != -1:
        return line_break

    sentence_breaks = [
        text.rfind(
            ". ",
            search_start,
            target_end,
        ),
        text.rfind(
            "! ",
            search_start,
            target_end,
        ),
        text.rfind(
            "? ",
            search_start,
            target_end,
        ),
    ]

    valid_breaks = [
        position + 1
        for position in sentence_breaks
        if position != -1
    ]

    if valid_breaks:
        return max(valid_breaks)

    return target_end