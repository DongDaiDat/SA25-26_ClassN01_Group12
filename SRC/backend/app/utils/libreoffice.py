import subprocess
from pathlib import Path
from app.core.config import settings

def convert_docx_to_pdf(docx_path: str, out_dir: str) -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.libreoffice_bin,
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        docx_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"LIBREOFFICE_CONVERT_FAILED: {r.stderr[:300]}")
    pdf_path = str(Path(out_dir) / (Path(docx_path).stem + ".pdf"))
    return pdf_path
