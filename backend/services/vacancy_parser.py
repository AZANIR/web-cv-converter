"""Parse vacancy input (text / URL / file) and templatize via AI into case study JSON."""

import ipaddress
import logging
import socket
from typing import Any
from urllib.parse import urlparse

import httpx

from core.ai_client import get_ai_client

logger = logging.getLogger(__name__)


def _validate_url(url: str) -> None:
    """Validate that a URL is safe to fetch (SSRF protection)."""
    parsed = urlparse(url)

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Only HTTP/HTTPS schemes are allowed, got: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must contain a valid hostname")

    # Try to interpret hostname as an IP address directly (covers numeric, hex, IPv6)
    # Handle hex-encoded IPs like 0x7f000001
    try:
        if hostname.startswith("0x") or hostname.startswith("0X"):
            addr = ipaddress.ip_address(int(hostname, 16))
        else:
            addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise ValueError(f"Internal/private IP addresses are not allowed: {hostname}")
        return
    except ValueError as e:
        if "Internal" in str(e):
            raise
        # Not a literal IP -- fall through to DNS resolution

    # Resolve hostname and check all resulting IPs
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {hostname}")

    for _, _, _, _, sockaddr in addrinfos:
        ip_str = sockaddr[0]
        addr = ipaddress.ip_address(ip_str)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise ValueError(f"Internal/private IP addresses are not allowed: {ip_str}")


def extract_text_from_url(url: str) -> str:
    """Fetch URL and extract main text content.

    This is intentionally synchronous so it can be safely used with
    ``asyncio.to_thread`` from async callers.
    """
    import trafilatura

    _validate_url(url)

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        resp = client.get(url)
        resp.raise_for_status()
    extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
    if not extracted:
        raise ValueError(f"Could not extract text content from URL: {url}")
    return extracted


def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from uploaded file bytes."""
    lower = filename.lower()
    if lower.endswith((".md", ".txt")):
        return content.decode("utf-8")
    if lower.endswith(".pdf"):
        from pypdf import PdfReader
        import io

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError("PDF contains no extractable text")
        return text
    raise ValueError(f"Unsupported file type: {filename}")


def templatize_vacancy(raw_text: str, prompt_content: str) -> dict[str, Any]:
    """Use AI to convert raw vacancy text into structured case study JSON."""
    delimited_text = f"<user_content>\n{raw_text}\n</user_content>"
    full_prompt = prompt_content.replace("{{VACANCY_TEXT}}", delimited_text)
    client = get_ai_client()
    return client.generate_json(full_prompt, temperature=0.2)
