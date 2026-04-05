import hashlib
import re
import uuid

from core.config import get_settings
from core.supabase import get_supabase

BUCKET = "cv-pdfs"


def _safe_filename_segment(segment: str, max_len: int = 120) -> str:
    """Supabase Storage: only use safe characters in object names."""
    out = "".join(c if c.isalnum() or c in "._-" else "_" for c in segment)
    out = re.sub(r"_+", "_", out).strip("._")
    return (out or "cv")[:max_len]


def _user_storage_prefix(user_id: str) -> str:
    """Hex-only prefix derived from user id — never contains Auth0 '|' or other invalid key chars."""
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:40]


def upload_pdf(pdf_bytes: bytes, user_id: str, base_filename: str) -> tuple[str, str]:
    safe_name = "".join(c for c in base_filename if c.isalnum() or c in "._- ")[:120] or "cv"
    if not safe_name.lower().endswith(".md"):
        pass
    pdf_filename = safe_name.rsplit(".", 1)[0] + ".pdf" if "." in safe_name else safe_name + ".pdf"
    pdf_filename = _safe_filename_segment(pdf_filename, max_len=120)
    prefix = _user_storage_prefix(user_id)
    storage_path = f"{prefix}/{uuid.uuid4()}/{pdf_filename}"

    sb = get_supabase()
    sb.storage.from_(BUCKET).upload(
        path=storage_path,
        file=pdf_bytes,
        file_options={"content-type": "application/pdf"},
    )
    return storage_path, pdf_filename


def get_signed_url(storage_path: str) -> str:
    s = get_settings()
    sb = get_supabase()
    result = sb.storage.from_(BUCKET).create_signed_url(
        storage_path, s.signed_url_expires_seconds
    )
    if isinstance(result, dict) and "signedURL" in result:
        return result["signedURL"]
    if isinstance(result, dict) and "signedUrl" in result:
        return result["signedUrl"]
    raise RuntimeError("Unexpected signed URL response")
