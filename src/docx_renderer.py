
from pathlib import Path
import win32com.client


def render_docx_to_pdf(
    docx_path: str | Path,
    pdf_path: str | Path,
) -> Path:
    """Convert a DOCX document to PDF using Microsoft Word."""
    source = Path(docx_path).resolve()
    destination = Path(pdf_path).resolve()

    if not source.is_file():
        raise FileNotFoundError(f"DOCX not found: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False

    try:
        document = word.Documents.Open(
            str(source),
            ReadOnly=True,
            AddToRecentFiles=False,
        )
        try:
            document.SaveAs2(
                str(destination),
                FileFormat=17,
            )
        finally:
            document.Close(False)
    finally:
        word.Quit()

    return destination
