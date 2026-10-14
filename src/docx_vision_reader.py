
from pathlib import Path

import pymupdf

from src.docx_renderer import render_docx_to_pdf
from src.image_reader import extract_from_image


def extract_docx_with_vision(file_path: str | Path) -> dict:
    """Render a DOCX to PDF and extract metadata from its first page."""

    source = Path(file_path)
    pdf_path = source.parent / f"{source.stem}_rendered.pdf"
    image_path = source.parent / f"{source.stem}_page.png"

    render_docx_to_pdf(source, pdf_path)

    try:
        with pymupdf.open(pdf_path) as pdf:
            if len(pdf) == 0:
                raise ValueError("The rendered PDF contains no pages.")

            page = pdf[0]
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )
            pixmap.save(str(image_path))

        return extract_from_image(image_path)

    finally:
        if pdf_path.exists():
            pdf_path.unlink()

        if image_path.exists():
            image_path.unlink()
