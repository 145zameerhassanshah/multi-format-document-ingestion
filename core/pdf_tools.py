import io

import pymupdf
from pypdf import PdfReader, PdfWriter
from PIL import Image
import pytesseract


def merge_pdfs(paths):
    """
    Merge multiple PDF files into one PDF.
    """

    writer = PdfWriter()

    for path in paths:
        writer.append(str(path))

    output = io.BytesIO()

    writer.write(output)
    writer.close()

    output.seek(0)

    return output.getvalue()


def split_pdf(path):
    """
    Split a PDF into individual page PDFs.
    """

    reader = PdfReader(str(path))

    outputs = []

    for page_number, page in enumerate(reader.pages, start=1):

        writer = PdfWriter()
        writer.add_page(page)

        buffer = io.BytesIO()

        writer.write(buffer)
        writer.close()

        buffer.seek(0)

        outputs.append(
            (
                f"page_{page_number}.pdf",
                buffer.getvalue()
            )
        )

    return outputs


def pdf_to_images(
    path,
    dpi=160,
    image_format="PNG"
):
    """
    Convert each PDF page into an image.
    """

    doc = pymupdf.open(str(path))

    scale = dpi / 72
    matrix = pymupdf.Matrix(scale, scale)

    results = []

    fmt = image_format.upper()

    ext = (
        "png"
        if fmt == "PNG"
        else "jpg"
    )

    try:
        for page_number, page in enumerate(doc, start=1):

            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                (pix.width, pix.height),
                pix.samples
            )

            buffer = io.BytesIO()

            image.save(
                buffer,
                format=fmt
            )

            buffer.seek(0)

            results.append(
                (
                    f"page_{page_number}.{ext}",
                    buffer.getvalue()
                )
            )

    finally:
        doc.close()

    return results


def extract_pdf_text(
    path,
    ocr_fallback=True,
    min_chars=40
):
    """
    Extract text from a PDF.

    Normal digital PDF:
        PyMuPDF extracts the existing text layer.

    Scanned/low-text page:
        Tesseract OCR is used as a fallback.
    """

    doc = pymupdf.open(str(path))

    pages = []
    ocr_pages = []

    try:
        for page_number, page in enumerate(doc, start=1):

            text = page.get_text(
                "text"
            ).strip()

            method = "pymupdf_text"

            if (
                ocr_fallback
                and len(text) < min_chars
            ):

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    (pix.width, pix.height),
                    pix.samples
                )

                text = pytesseract.image_to_string(
                    image
                ).strip()

                method = "tesseract_ocr"

                ocr_pages.append(
                    page_number
                )

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                    "method": method
                }
            )

        metadata = dict(
            doc.metadata or {}
        )

    finally:
        doc.close()

    return {
        "text": "\n\n".join(
            page["text"]
            for page in pages
        ),
        "pages": pages,
        "page_count": len(pages),
        "ocr_pages": ocr_pages,
        "metadata": metadata,
    }