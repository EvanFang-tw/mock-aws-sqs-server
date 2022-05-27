from hashlib import sha256
import hmac


def sha256_hex(text: str) -> str:
    """
    Hash text by SHA256.
    """
    return sha256(text.encode("utf-8")).hexdigest()


def hmac_sha256(secret: bytes, text: str):
    """
    Encrypt text by HMAC-SHA256.
    """
    return hmac.new(secret, text.encode("utf-8"), sha256).digest()
