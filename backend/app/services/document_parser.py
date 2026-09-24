from io import BytesIO
from pathlib import PurePosixPath
import re
import pymupdf
from docx import Document

from dataclasses import dataclass


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


@dataclass
class ExtractedPage:
    text: str
    page_number: int | None = None
    section: str | None = None


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


def extract_pdf_text(
    content: bytes,
) -> str:
    pages = extract_pdf_pages(
        content
    )

    return "\n\n".join(
        f"[Page {page.page_number}]\n{page.text}"
        if page.page_number is not None
        else page.text
        for page in pages
    )


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


def extract_pages(
    filename: str,
    content: bytes,
) -> list[ExtractedPage]:
    extension = PurePosixPath(
        filename
    ).suffix.lower()

    if extension in {
        ".md",
        ".txt",
    }:
        text = extract_text_file(content)

        return [
            ExtractedPage(
                text=text,
            )
        ]

    if extension == ".pdf":
        return extract_pdf_pages(content)

    if extension == ".docx":
        text = extract_docx_text(content)

        return [
            ExtractedPage(
                text=text,
            )
        ]

    if extension == ".md":
        return extract_markdown_pages(
            content
        )

    if extension == ".txt":
        return [
            ExtractedPage(
                text=extract_text_file(
                    content
                ),
            )
        ]

    raise ValueError(
        f"Unsupported document format: "
        f"{extension or 'unknown'}"
    )


def extract_pdf_pages(
    content: bytes,
) -> list[ExtractedPage]:
    document = pymupdf.open(
        stream=content,
        filetype="pdf",
    )

    try:
        pages: list[ExtractedPage] = []

        for page_number, page in enumerate(
            document,
            start=1,
        ):
            text = page.get_text().strip()

            if not text:
                continue

            pages.append(
                ExtractedPage(
                    text=text,
                    page_number=page_number,
                )
            )

        return pages

    finally:
        document.close()


def detect_markdown_sections(
    text: str,
) -> list[tuple[str | None, str]]:
    lines = text.splitlines()

    sections: list[
        tuple[str | None, str]
    ] = []

    current_section: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if not current_lines:
            return

        content = "\n".join(
            current_lines
        ).strip()

        if content:
            sections.append(
                (
                    current_section,
                    content,
                )
            )

    for line in lines:
        heading = re.match(
            r"^#{1,6}\s+(.+)$",
            line.strip(),
        )

        if heading:
            flush()

            current_section = (
                heading.group(1).strip()
            )

            current_lines = [
                line
            ]

            continue

        current_lines.append(line)

    flush()

    return sections


def extract_markdown_pages(
    content: bytes,
) -> list[ExtractedPage]:
    text = extract_text_file(
        content
    )

    sections = (
        detect_markdown_sections(text)
    )

    return [
        ExtractedPage(
            text=section_text,
            section=section_name,
        )
        for section_name, section_text
        in sections
    ]


