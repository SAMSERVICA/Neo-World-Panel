from __future__ import annotations
import base64
import hashlib
import hmac
import secrets
import struct
import time
import urllib.parse

def generate_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")

def _b32decode(secret: str) -> bytes:
    pad = (8 - len(secret) % 8) % 8
    return base64.b32decode(secret.upper() + "=" * pad)

def _code_at(secret: str, counter: int) -> str:
    digest = hmac.new(_b32decode(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"

def verify(secret: str, code: str, window: int = 1) -> bool:
    code = (code or "").strip()
    if len(code) != 6 or not code.isdigit():
        return False
    counter = int(time.time() // 30)
    for c in range(counter - window, counter + window + 1):
        if hmac.compare_digest(_code_at(secret, c), code):
            return True
    return False

def otpauth_uri(secret: str, label: str = "Neo World") -> str:
    return ("otpauth://totp/" + urllib.parse.quote(label)
            + f"?secret={secret}&issuer=NeoWorld&algorithm=SHA1&digits=6&period=30")
