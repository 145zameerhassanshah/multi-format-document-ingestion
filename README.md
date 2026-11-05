# DocForge AI

A local-first personal document processing suite for OCR, PDF utilities and offline conversion.

## Phase 1 features

- OCR image → text
- OCR scanned PDF → text
- PDF text extraction with OCR fallback
- Merge PDFs
- Split PDF
- Images → PDF
- PDF → images
- TXT/text → PDF
- DOCX → PDF using local LibreOffice
- PDF → editable text-oriented DOCX

## Run

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### OCR dependency

Install Tesseract OCR locally and add it to PATH.

### Word → PDF dependency

Install LibreOffice locally. DocForge calls LibreOffice in headless mode, so no paid conversion API is required.

## Privacy

Core conversion logic is intended to run on your own machine. Files do not need to be uploaded to a third-party conversion service.

## Architecture

```text
UI (Streamlit)
    ↓
Core modules
    ├── OCR
    ├── PDF tools
    └── Converters
    ↓
Local open-source engines/libraries
```

## Next planned features

- searchable PDF (OCR text layer while preserving original scan)
- PDF compression
- page reorder/delete/rotate
- batch conversion queue
- better PDF → Word layout reconstruction
- document preview
- signature/stamp-aware workflows
- optional local AI features
