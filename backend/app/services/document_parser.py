from io import BytesIO
from pathlib import PurePosixPath

import pymupdf
from docx import Document


SUPPORTED_TEXT_EXTENSIONS = {
    ".md",
    ".txt",
}

SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".md",
    ".txt",
    ".pdf",
    ".docx",
}


def extract_text(filename: str, content: bytes) -> str:
    extension = PurePosixPath(filename).suffix.lower()

    if extension in SUPPORTED_TEXT_EXTENSIONS:
        return extract_text_file(content)

    if extension == ".pdf":
        return extract_pdf_text(content)

    if extension == ".docx":
        return extract_docx_text(content)

    raise ValueError(
        f"Unsupported document format: {extension or 'unknown'}"
    )


def extract_text_file(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def extract_pdf_text(content: bytes) -> str:
    document = pymupdf.open(
        stream=content,
        filetype="pdf",
    )

    try:
        pages: list[str] = []

        for page_number, page in enumerate(
            document,
            start=1,
        ):
            text = page.get_text().strip()

            if not text:
                continue

            pages.append(
                f"[Page {page_number}]\n{text}"
            )

        return "\n\n".join(pages)

    finally:
        document.close()


def extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))

    sections: list[str] = []

    # Paragraphs
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            sections.append(text)

    # Tables
    for table in document.tables:
        rows: list[str] = []

        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            rows.append(" | ".join(cells))

        if rows:
            sections.append(
                "[Table]\n" + "\n".join(rows)
            )

    return "\n\n".join(sections)