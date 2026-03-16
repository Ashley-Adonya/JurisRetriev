from __future__ import annotations

from pymongo.errors import DuplicateKeyError

from . import auth_store
from .security import generate_token, hash_password, verify_password, validate_password_complexity


def register_user(email: str, password: str) -> dict:
    is_valid, message = validate_password_complexity(password)
    if not is_valid:
        raise ValueError(message)

    pwd_hash = hash_password(password)

    try:
        user = auth_store.create_user(email=email, password_hash=pwd_hash)
    except DuplicateKeyError as exc:
        raise ValueError("email déjà utilisé") from exc

    verification_token = generate_token()
    auth_store.create_email_verification_token(user["_id"], verification_token)

    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "email_verified": False,
        "verification_token": verification_token,
    }


def verify_email(token: str) -> bool:
    token_doc = auth_store.consume_email_verification_token(token)
    if not token_doc:
        return False
    return auth_store.mark_email_verified(token_doc["user_id"])


def request_email_verification_resend(email: str) -> dict:
    user = auth_store.find_user_by_email(email)
    if not user:
        return {"ok": True, "sent": False}

    if not user.get("is_active", True):
        return {"ok": True, "sent": False}

    if user.get("email_verified", False):
        return {"ok": True, "sent": False}

    token = generate_token()
    auth_store.create_email_verification_token(user["_id"], token)
    return {
        "ok": True,
        "sent": True,
        "email": user.get("email"),
        "token": token,
    }


def request_password_reset(email: str) -> dict:
    user = auth_store.find_user_by_email(email)
    if not user:
        return {"ok": True, "sent": False}

    if not user.get("is_active", True):
        return {"ok": True, "sent": False}

    token = generate_token()
    auth_store.create_password_reset_token(user["_id"], token)

    return {
        "ok": True,
        "sent": True,
        "email": user.get("email"),
        "token": token,
    }


def reset_password_with_token(token: str, new_password: str) -> dict:
    is_valid, message = validate_password_complexity(new_password)
    if not is_valid:
        return {"ok": False, "reason": "weak_password", "message": message}

    token_doc = auth_store.consume_password_reset_token(token)
    if not token_doc:
        return {"ok": False, "reason": "invalid_or_expired_token"}

    password_hash = hash_password(new_password)
    updated = auth_store.update_user_password(token_doc["user_id"], password_hash)
    if not updated:
        return {"ok": False, "reason": "user_not_found"}

    return {"ok": True}


def authenticate(email: str, password: str) -> dict:
    attempts = auth_store.get_login_attempt_window(email=email, window_minutes=15)
    if attempts.get("failures", 0) >= 5:
        return {
            "ok": False,
            "reason": "too_many_attempts",
            "message": "Trop de tentatives échouées. Réessayez dans quelques minutes.",
        }

    user = auth_store.find_user_by_email(email)
    if not user:
        auth_store.record_login_attempt(email=email, success=False)
        return {"ok": False, "reason": "invalid_credentials"}

    if not verify_password(password, user["password_hash"]):
        auth_store.record_login_attempt(email=email, success=False)
        return {"ok": False, "reason": "invalid_credentials"}

    if not user.get("email_verified", False):
        auth_store.record_login_attempt(email=email, success=True)
        return {"ok": False, "reason": "email_not_verified"}

    auth_store.record_login_attempt(email=email, success=True)
    return {
        "ok": True,
        "user_id": str(user["_id"]),
        "email": user["email"],
    }


def consume_quota(user_id: str, feature: str, limit: int, window_seconds: int = 86_400) -> dict:
    return auth_store.increment_usage(
        user_id=user_id,
        feature=feature,
        limit=limit,
        window_seconds=window_seconds,
    )
