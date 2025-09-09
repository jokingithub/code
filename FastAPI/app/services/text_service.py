import subprocess
from PyPDF2 import PdfReader
import docx2txt

def extract_doc_with_antiword(path: str) -> str:
    try:
        result = subprocess.run(
            ["antiword", path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"antiword failed: {e.stderr}")

def extract_docx(path: str) -> str:
    return docx2txt.process(path)

def extract_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)
