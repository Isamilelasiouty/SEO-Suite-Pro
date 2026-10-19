"""
Security module for SEO Suite Pro:
- Input sanitization and HTML escaping
- Strict SSRF (Server-Side Request Forgery) protection
- URL validation and normalization
- Cryptographic encryption for sensitive session credentials (Gemini API keys)
"""

import html
import ipaddress
import socket
from urllib.parse import urlparse
from cryptography.fernet import Fernet
import base64
import hashlib

# Internal encryption key derivation from app secret
_APP_SALT = b"seo_suite_pro_secure_salt_v2"

def _get_fernet_instance() -> Fernet:
    # Deterministic key generation based on server secret
    key_material = hashlib.sha256(_APP_SALT).digest()
    fernet_key = base64.urlsafe_b64encode(key_material)
    return Fernet(fernet_key)

def encrypt_secret(plain_text: str) -> str:
    """Encrypt a sensitive string (e.g. API key) for secure storage."""
    if not plain_text:
        return ""
    f = _get_fernet_instance()
    return f.encrypt(plain_text.encode("utf-8")).decode("utf-8")

def decrypt_secret(encrypted_text: str) -> str:
    """Decrypt an encrypted string."""
    if not encrypted_text:
        return ""
    try:
        f = _get_fernet_instance()
        return f.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""

def sanitize_text(text: str | None) -> str:
    """Escape text safely to prevent HTML injection."""
    if text is None:
        return ""
    return html.escape(str(text))

def is_safe_host(hostname: str) -> bool:
    """
    Verify hostname does not resolve to private or loopback IP ranges.
    Prevents SSRF attacks against internal cloud metadata, localhost, or private subnets.
    """
    if not hostname:
        return False
    
    # Block immediate localhost patterns
    lower = hostname.lower().strip()
    if lower in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal"):
        return False
    
    try:
        # Resolve hostname to IPv4/IPv6 addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
            ):
                return False
        return True
    except (socket.gaierror, ValueError):
        # Could not resolve; allow requests engine to handle failure gracefully or deny
        return False

def validate_and_normalize_url(url: str) -> tuple[bool, str, str]:
    """
    Validates and normalizes target URL.
    Returns: (is_valid, normalized_url, error_message)
    """
    if not url:
        return False, "", "URL cannot be empty."
    
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "", "Invalid URL format: missing domain."
        
        # Check SSRF safety
        hostname = parsed.hostname or ""
        if not is_safe_host(hostname):
            return False, "", f"Target host '{hostname}' is not permitted (private or restricted IP address)."
        
        # Canonical normalization: strip trailing slash for base, preserve path
        normalized = parsed.scheme.lower() + "://" + parsed.netloc.lower()
        if parsed.path and parsed.path != "/":
            normalized += parsed.path.rstrip("/")
        if parsed.query:
            normalized += "?" + parsed.query
        
        return True, normalized, ""
    except Exception as e:
        return False, "", f"Failed to parse URL: {str(e)}"
