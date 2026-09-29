from pathlib import Path
from pypdf import PdfReader

MAX_SOURCE_CHARS = 30000


def read_uploaded_file(uploaded_file) -> str:
    """Read PDF, TXT, or Markdown files uploaded through Streamlit."""
    if uploaded_file is None:
        return ""

    suffix = Path(uploaded_file.name).suffix.lower()

    try:
        if suffix == ".pdf":
            reader = PdfReader(uploaded_file)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        elif suffix in {".txt", ".md"}:
            text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        else:
            return ""

        return text[:MAX_SOURCE_CHARS]

    except Exception as exc:
        raise RuntimeError(f"Could not read uploaded file: {exc}") from exc


def combine_source_text(notes: str, file_text: str) -> str:
    """Combine pasted notes and uploaded-file text safely."""
    parts = [part.strip() for part in [notes or "", file_text or ""] if part and part.strip()]
    return "\n\n".join(parts)[:MAX_SOURCE_CHARS]
