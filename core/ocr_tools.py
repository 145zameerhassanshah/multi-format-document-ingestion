from PIL import Image
import pymupdf
import pytesseract


def ocr_image(path, language="eng"):
    """
    Extract text from an image using Tesseract OCR.
    """

    with Image.open(path) as image:
        text = pytesseract.image_to_string(
            image,
            lang=language
        )

        return {
            "text": text.strip(),
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
        }


def ocr_pdf(path, language="eng", dpi=200):
    """
    Convert each PDF page to an image and run Tesseract OCR.

    Useful for scanned PDFs that do not contain a real text layer.
    """

    doc = pymupdf.open(str(path))

    scale = dpi / 72
    matrix = pymupdf.Matrix(scale, scale)

    pages = []

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

            text = pytesseract.image_to_string(
                image,
                lang=language
            ).strip()

            pages.append({
                "page": page_number,
                "text": text,
                "method": "tesseract_ocr"
            })

    finally:
        doc.close()

    return {
        "text": "\n\n".join(
            page["text"] for page in pages
        ),
        "pages": pages,
        "page_count": len(pages),
        "language": language,
        "dpi": dpi,
    }