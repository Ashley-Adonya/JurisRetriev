from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import re


def validate_password_complexity(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Le mot de passe est requis."
    if len(password) < 12:
        return False, "Le mot de passe doit contenir au moins 12 caractères."
    if not re.search(r"[A-Z]", password):
        return False, "Le mot de passe doit contenir au moins une lettre majuscule."
    if not re.search(r"[a-z]", password):
        return False, "Le mot de passe doit contenir au moins une lettre minuscule."
    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial."
    return True, "ok"


def hash_password(password: str, iterations: int = 210_000) -> str:
    if not password:
        raise ValueError("password vide")

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    digest_b64 = base64.b64encode(digest).decode("utf-8")
    return f"pbkdf2_sha256${iterations}${salt_b64}${digest_b64}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iter_str, salt_b64, digest_b64 = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64.encode("utf-8"))
        expected = base64.b64decode(digest_b64.encode("utf-8"))

        current = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(current, expected)
    except Exception:
        return False


def generate_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


__all__ = ["hash_password", "verify_password", "generate_token", "validate_password_complexity"]
