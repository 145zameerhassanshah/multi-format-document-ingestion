from pathlib import Path
import tempfile
import uuid

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    temp_dir = Path(tempfile.gettempdir()) / "docforge_ai"
    temp_dir.mkdir(parents=True, exist_ok=True)
    path = temp_dir / f"{uuid.uuid4().hex}{suffix}"
    path.write_bytes(uploaded_file.getbuffer())
    return path

def safe_output_name(name: str, suffix: str):
    stem = Path(name).stem.replace(" ", "_")
    return f"{stem}{suffix}"
