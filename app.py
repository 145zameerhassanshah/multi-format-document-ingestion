import io
import json
import zipfile
from pathlib import Path

import streamlit as st

from core.utils import save_uploaded_file, safe_output_name
from core.pdf_tools import merge_pdfs, split_pdf, pdf_to_images, extract_pdf_text
from core.ocr_tools import ocr_image, ocr_pdf
from core.converters import images_to_pdf, txt_to_pdf, docx_to_pdf, pdf_to_docx


st.set_page_config(
    page_title="DocForge AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
    --bg: #07111f;
    --panel: #0d1b2d;
    --panel-soft: #10233b;
    --line: rgba(148, 163, 184, .16);
    --text: #edf5ff;
    --muted: #98abc3;
    --accent: #4ea8ff;
    --accent2: #7c9cff;
    --success: #43d19e;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 12% 8%, rgba(78,168,255,.12), transparent 25%),
      radial-gradient(circle at 82% 0%, rgba(124,156,255,.10), transparent 24%),
      var(--bg);
}
[data-testid="stSidebar"] {
    background: #081524;
    border-right: 1px solid var(--line);
}
.block-container {
    max-width: 1450px;
    padding-top: 1.6rem;
    padding-bottom: 4rem;
}
html, body, [class*="css"] {
    color: var(--text);
}
.hero {
    border: 1px solid var(--line);
    border-radius: 24px;
    padding: 28px 30px;
    background: linear-gradient(135deg, rgba(16,35,59,.98), rgba(9,25,43,.96));
    box-shadow: 0 24px 70px rgba(0,0,0,.22);
    margin-bottom: 22px;
}
.hero-kicker {
    color: #78bcff;
    font-weight: 700;
    font-size: .78rem;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.hero h1 {
    margin: 8px 0 8px;
    font-size: 2.45rem;
    letter-spacing: -.04em;
}
.hero p {
    color: var(--muted);
    max-width: 800px;
    font-size: 1.02rem;
    margin-bottom: 0;
}
.badge {
    display: inline-block;
    border: 1px solid rgba(67,209,158,.25);
    background: rgba(67,209,158,.09);
    color: #76e7be;
    border-radius: 999px;
    padding: 6px 11px;
    font-size: .78rem;
    font-weight: 700;
    margin-top: 15px;
}
.tool-card {
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 18px;
    background: rgba(13,27,45,.86);
    min-height: 145px;
}
.tool-card h3 {margin:0 0 6px;font-size:1.05rem}
.tool-card p {margin:0;color:var(--muted);font-size:.88rem;line-height:1.45}
.section-title {
    margin-top: 22px;
    margin-bottom: 8px;
    font-size: 1.22rem;
    font-weight: 800;
}
.small-note {
    color: var(--muted);
    font-size: .86rem;
}
div[data-testid="stFileUploader"] {
    border: 1px dashed rgba(78,168,255,.35);
    border-radius: 18px;
    padding: 8px;
    background: rgba(13,27,45,.52);
}
.stButton > button, .stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid rgba(78,168,255,.25);
    font-weight: 700;
}
hr {border-color: var(--line);}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

TOOLS = {
    "🏠 Dashboard": "dashboard",
    "🔎 OCR & Scan": "ocr",
    "📚 Merge PDFs": "merge",
    "✂️ Split PDF": "split",
    "🖼️ Images → PDF": "images_pdf",
    "🧩 PDF → Images": "pdf_images",
    "📝 Word → PDF": "word_pdf",
    "📄 PDF → Word": "pdf_word",
    "📃 Text → PDF": "text_pdf",
    "🧠 Extract Text": "extract_text",
}

st.sidebar.markdown("## ◈ DocForge AI")
st.sidebar.caption("Private offline document workspace")
selected_label = st.sidebar.radio("TOOLS", list(TOOLS.keys()), label_visibility="collapsed")
tool = TOOLS[selected_label]
st.sidebar.divider()
st.sidebar.markdown("**Privacy**")
st.sidebar.caption("Designed for local processing. No cloud API is required for the included core tools.")
st.sidebar.markdown("**Status**  \n🟢 Core workspace")

st.markdown("""
<div class="hero">
  <div class="hero-kicker">Personal Offline Document Suite</div>
  <h1>DocForge AI</h1>
  <p>Convert, extract, merge, split and OCR documents from one clean workspace — with a local-first architecture and no per-file subscription.</p>
  <span class="badge">● Processed locally</span>
</div>
""", unsafe_allow_html=True)


def zip_named_files(items):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    buf.seek(0)
    return buf.getvalue()


if tool == "dashboard":
    st.markdown('<div class="section-title">Workspace</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cards = [
        ("🔎", "OCR & Scanned Docs", "Extract text from images and scanned PDFs with local OCR."),
        ("⇄", "File Conversion", "Convert images, text, Word and PDF between useful formats."),
        ("▱", "PDF Toolkit", "Merge, split, render pages and inspect document content."),
        ("🔐", "Local-First", "Your architecture is designed to work without paid conversion APIs."),
    ]
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="tool-card">
              <div style="font-size:1.5rem;margin-bottom:10px">{icon}</div>
              <h3>{title}</h3><p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Build roadmap</div>', unsafe_allow_html=True)
    st.markdown("""
    **Phase 1 — Core:** OCR, PDF merge/split, image/PDF conversion, text extraction, Word/PDF conversion.  
    **Phase 2 — Smart documents:** searchable PDF, compression, batch jobs, signatures/stamps preservation workflows.  
    **Phase 3 — AI:** layout analysis, document classification, semantic search and optional RAG.
    """)

elif tool == "ocr":
    st.subheader("OCR & Scanned Documents")
    mode = st.radio("Source", ["Image", "Scanned PDF"], horizontal=True)
    types = ["png","jpg","jpeg","tif","tiff","bmp","webp"] if mode == "Image" else ["pdf"]
    file = st.file_uploader("Drop a scan or image", type=types)

    if file and st.button("Run OCR", type="primary"):
        path = save_uploaded_file(file)
        with st.spinner("Reading document locally..."):
            result = ocr_image(path) if mode == "Image" else ocr_pdf(path)
        st.success("OCR complete")
        st.text_area("Extracted text", result["text"], height=360)
        st.download_button("Download TXT", result["text"], safe_output_name(file.name, ".txt"), "text/plain")
        st.download_button(
            "Download JSON",
            json.dumps(result, indent=2, ensure_ascii=False),
            safe_output_name(file.name, ".json"),
            "application/json",
        )

elif tool == "merge":
    st.subheader("Merge PDFs")
    files = st.file_uploader("Add PDFs in the order you want to merge", type=["pdf"], accept_multiple_files=True)
    if files and len(files) >= 2 and st.button("Merge PDFs", type="primary"):
        paths = [save_uploaded_file(f) for f in files]
        data = merge_pdfs(paths)
        st.success(f"Merged {len(files)} PDFs")
        st.download_button("Download merged PDF", data, "merged_document.pdf", "application/pdf")

elif tool == "split":
    st.subheader("Split PDF")
    file = st.file_uploader("Upload a PDF", type=["pdf"])
    if file and st.button("Split into pages", type="primary"):
        parts = split_pdf(save_uploaded_file(file))
        z = zip_named_files(parts)
        st.success(f"Created {len(parts)} page PDFs")
        st.download_button("Download pages as ZIP", z, safe_output_name(file.name, "_pages.zip"), "application/zip")

elif tool == "images_pdf":
    st.subheader("Images → PDF")
    files = st.file_uploader("Upload one or more images", type=["png","jpg","jpeg","tif","tiff","bmp","webp"], accept_multiple_files=True)
    if files and st.button("Create PDF", type="primary"):
        paths = [save_uploaded_file(f) for f in files]
        data = images_to_pdf(paths)
        st.success(f"Created PDF from {len(files)} image(s)")
        st.download_button("Download PDF", data, "images_combined.pdf", "application/pdf")

elif tool == "pdf_images":
    st.subheader("PDF → Images")
    file = st.file_uploader("Upload a PDF", type=["pdf"])
    dpi = st.slider("Render quality (DPI)", 96, 300, 160, 16)
    if file and st.button("Convert pages", type="primary"):
        images = pdf_to_images(save_uploaded_file(file), dpi=dpi)
        z = zip_named_files(images)
        st.success(f"Converted {len(images)} page(s)")
        st.download_button("Download images as ZIP", z, safe_output_name(file.name, "_images.zip"), "application/zip")

elif tool == "word_pdf":
    st.subheader("Word → PDF")
    st.caption("Uses locally installed LibreOffice for offline conversion.")
    file = st.file_uploader("Upload DOCX", type=["docx"])
    if file and st.button("Convert to PDF", type="primary"):
        try:
            data = docx_to_pdf(save_uploaded_file(file))
            st.success("Conversion complete")
            st.download_button("Download PDF", data, safe_output_name(file.name, ".pdf"), "application/pdf")
        except Exception as e:
            st.error(str(e))

elif tool == "pdf_word":
    st.subheader("PDF → Word")
    st.caption("Creates an editable text-oriented DOCX. Complex layouts may need later layout-aware reconstruction.")
    file = st.file_uploader("Upload PDF", type=["pdf"])
    if file and st.button("Convert to DOCX", type="primary"):
        data = pdf_to_docx(save_uploaded_file(file))
        st.success("DOCX created")
        st.download_button(
            "Download DOCX",
            data,
            safe_output_name(file.name, ".docx"),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

elif tool == "text_pdf":
    st.subheader("Text → PDF")
    text = st.text_area("Paste text", height=320)
    if text.strip() and st.button("Create PDF", type="primary"):
        data = txt_to_pdf(text)
        st.download_button("Download PDF", data, "document.pdf", "application/pdf")

elif tool == "extract_text":
    st.subheader("Extract Text from PDF")
    file = st.file_uploader("Upload digital or scanned PDF", type=["pdf"])
    ocr = st.toggle("Use OCR fallback for scan-like pages", value=True)
    if file and st.button("Extract text", type="primary"):
        result = extract_pdf_text(save_uploaded_file(file), ocr_fallback=ocr)
        st.metric("Pages", result["page_count"])
        st.caption(f"OCR fallback pages: {result['ocr_pages'] or 'None'}")
        st.text_area("Extracted text", result["text"], height=360)
        st.download_button("Download TXT", result["text"], safe_output_name(file.name, ".txt"), "text/plain")
        st.download_button(
            "Download structured JSON",
            json.dumps(result, indent=2, ensure_ascii=False),
            safe_output_name(file.name, ".json"),
            "application/json",
        )

st.divider()
st.caption("DocForge AI • Local-first document processing • Phase 1")
