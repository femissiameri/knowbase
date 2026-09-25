import re


STOP_WORDS = {
    # English
    "what",
    "does",
    "do",
    "is",
    "are",
    "the",
    "a",
    "an",
    "mean",
    "means",
    "of",
    "for",
    "in",
    "to",
    "and",
    "or",
    "how",
    "why",
    "where",
    "when",

    # French
    "que",
    "quoi",
    "est",
    "sont",
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "de",
    "du",
    "pour",
    "dans",
    "et",
    "ou",
    "comment",
    "pourquoi",

    # German
    "was",
    "ist",
    "sind",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "und",
    "oder",
    "wie",
    "warum",
    "bedeutet",
}



def build_fts_query(query: str) -> str:
    phrases = re.findall(r'"([^"]+)"', query)

    remaining = re.sub(r'"[^"]+"', " ", query)

    words = re.findall(r"\b[\wÀ-ÿ]+\b", remaining.lower())

    words = [
        word
        for word in words
        if word not in STOP_WORDS and len(word) >= 2
    ]

    fts_parts: list[str] = []

    for phrase in phrases:
        phrase = phrase.strip().replace('"', '""')

        if phrase:
            fts_parts.append(f'"{phrase}"')

    for word in words:
        word = word.replace('"', '""')
        fts_parts.append(word)

    # Remove duplicates while preserving order.
    return " OR ".join(dict.fromkeys(fts_parts))