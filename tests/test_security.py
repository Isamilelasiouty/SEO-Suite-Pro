"""
Unit tests for security, SSRF protection, URL validation, and encryption.
"""

from core.security import (
    decrypt_secret,
    encrypt_secret,
    is_safe_host,
    sanitize_text,
    validate_and_normalize_url,
)

def test_url_normalization():
    is_v, norm, _ = validate_and_normalize_url("example.com/path/")
    assert is_v is True
    assert norm == "https://example.com/path"

def test_ssrf_protection():
    assert is_safe_host("127.0.0.1") is False
    assert is_safe_host("localhost") is False
    assert is_safe_host("169.254.169.254") is False
    assert is_safe_host("10.0.0.5") is False
    assert is_safe_host("192.168.1.1") is False

def test_encryption_roundtrip():
    secret = "AIzaSySecretGeminiKey123456"
    encrypted = encrypt_secret(secret)
    assert encrypted != secret
    decrypted = decrypt_secret(encrypted)
    assert decrypted == secret

def test_html_sanitization():
    unsafe = "<script>alert('xss')</script>"
    safe = sanitize_text(unsafe)
    assert "<script>" not in safe
    assert "&lt;script&gt;" in safe
