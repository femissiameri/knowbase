from pathlib import Path

from app.services.document_parser import extract_text


pdf_path = Path(
    "../test-project/sample.pdf"
)

content = pdf_path.read_bytes()

text = extract_text(
    pdf_path.name,
    content,
)

print("Characters:", len(text))
print()
print(text[:2000])