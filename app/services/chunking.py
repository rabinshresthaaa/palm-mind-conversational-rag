import re


def fixed_size_chunking(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size.")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def sentence_aware_chunking(
    text: str,
    chunk_size: int = 1000,
) -> list[str]:
    """Group sentences into chunks without splitting them unnecessarily."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    text = text.strip()
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            # Split an unusually long sentence to respect the size limit.
            chunks.extend(
                fixed_size_chunking(sentence, chunk_size, overlap=0)
            )
            continue

        candidate = f"{current} {sentence}".strip()

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks


def chunk_text(
    text: str,
    strategy: str = "fixed",
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Choose a chunking strategy."""
    if strategy == "fixed":
        return fixed_size_chunking(text, chunk_size, overlap)
    if strategy == "sentence":
        return sentence_aware_chunking(text, chunk_size)

    raise ValueError(
        "Unknown strategy. Use 'fixed' or 'sentence'."
    )
