from pathlib import Path
import io
import shutil
import subprocess
import tempfile

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
import pymupdf


def images_to_pdf(paths):
    """
    Convert one or more images into a single PDF.
    """

    images = []

    try:
        for file_path in paths:
            with Image.open(file_path) as img:
                images.append(img.convert("RGB").copy())

        if not images:
            raise ValueError("No images provided.")

        output = io.BytesIO()

        first, rest = images[0], images[1:]

        first.save(
            output,
            format="PDF",
            save_all=True,
            append_images=rest,
            resolution=150.0,
        )

        output.seek(0)
        return output.getvalue()

    finally:
        for img in images:
            img.close()


def txt_to_pdf(text):
    """
    Convert plain text into a basic PDF.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    output = io.BytesIO()

    pdf = canvas.Canvas(output, pagesize=A4)

    _, height = A4

    x = 50
    y = height - 50

    line_height = 15
    max_chars = 95

    for paragraph in text.splitlines() or [""]:

        words = paragraph.split()
        line = ""

        if not words:
            y -= line_height

            if y < 50:
                pdf.showPage()
                y = height - 50

            continue

        for word in words:

            candidate = f"{line} {word}".strip()

            if len(candidate) > max_chars:

                if line:
                    pdf.drawString(x, y, line)

                y -= line_height

                if y < 50:
                    pdf.showPage()
                    y = height - 50

                line = word

            else:
                line = candidate

        if line:
            pdf.drawString(x, y, line)

            y -= line_height

            if y < 50:
                pdf.showPage()
                y = height - 50

    pdf.save()

    output.seek(0)

    return output.getvalue()


def find_libreoffice():
    """
    Try to locate LibreOffice automatically on Windows/Linux/macOS.
    """

    candidates = [
        shutil.which("libreoffice"),
        shutil.which("soffice"),
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    return None


def docx_to_pdf(path):
    """
    Convert DOCX to PDF using locally installed LibreOffice.

    No paid API is required.
    """

    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"DOCX file not found: {input_path}"
        )

    office = find_libreoffice()

    if not office:
        raise RuntimeError(
            "LibreOffice was not found. "
            "Install LibreOffice or add soffice.exe to your system PATH."
        )

    with tempfile.TemporaryDirectory() as tmp:

        command = [
            office,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            tmp,
            str(input_path),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
        )

        output_path = Path(tmp) / f"{input_path.stem}.pdf"

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr
                or result.stdout
                or "LibreOffice DOCX conversion failed."
            )

        if not output_path.exists():
            raise RuntimeError(
                "LibreOffice completed but no PDF output was generated."
            )

        return output_path.read_bytes()


def pdf_to_docx(path):
    """
    Convert a text-based PDF into an editable DOCX.

    Important:
    This is a text-oriented conversion.
    Complex layouts, tables, columns, images, signatures,
    and exact formatting may not be reproduced perfectly.
    """

    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {input_path}"
        )

    pdf = pymupdf.open(str(input_path))
    docx = Document()

    try:
        for page_number, page in enumerate(pdf, start=1):

            if page_number > 1:
                docx.add_page_break()

            text = page.get_text("text").strip()

            docx.add_heading(
                f"Page {page_number}",
                level=2
            )

            if not text:
                docx.add_paragraph(
                    "[No selectable text found on this page.]"
                )
                continue

            paragraphs = [
                paragraph.strip()
                for paragraph in text.split("\n\n")
                if paragraph.strip()
            ]

            if not paragraphs:
                paragraphs = [
                    line.strip()
                    for line in text.splitlines()
                    if line.strip()
                ]

            for paragraph in paragraphs:
                docx.add_paragraph(paragraph)

    finally:
        pdf.close()

    output = io.BytesIO()

    docx.save(output)

    output.seek(0)

    return output.getvalue()