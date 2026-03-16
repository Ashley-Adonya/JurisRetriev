from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from .mongodb import get_collection, utc_now


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def create_user(email: str, password_hash: str) -> dict:
    now = utc_now()
    doc = {
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "email_verified": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    result = get_collection("users").insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def find_user_by_email(email: str) -> dict | None:
    return get_collection("users").find_one({"email": email.strip().lower()})


def find_user_by_id(user_id: str | ObjectId) -> dict | None:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    return get_collection("users").find_one({"_id": oid})


def mark_email_verified(user_id: str | ObjectId) -> bool:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    result = get_collection("users").update_one(
        {"_id": oid},
        {"$set": {"email_verified": True, "updated_at": utc_now()}},
    )
    return result.modified_count == 1


def create_email_verification_token(user_id: str | ObjectId, token: str, ttl_minutes: int = 30) -> dict:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    now = utc_now()
    doc = {
        "user_id": oid,
        "token": token,
        "created_at": now,
        "expires_at": now + timedelta(minutes=ttl_minutes),
        "used_at": None,
    }
    get_collection("email_verification_tokens").insert_one(doc)
    return doc


def consume_email_verification_token(token: str) -> dict | None:
    now = utc_now()
    return get_collection("email_verification_tokens").find_one_and_update(
        {
            "token": token,
            "used_at": None,
            "expires_at": {"$gt": now},
        },
        {"$set": {"used_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def create_password_reset_token(user_id: str | ObjectId, token: str, ttl_minutes: int = 30) -> dict:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    now = utc_now()
    doc = {
        "user_id": oid,
        "token": token,
        "created_at": now,
        "expires_at": now + timedelta(minutes=ttl_minutes),
        "used_at": None,
    }
    get_collection("password_reset_tokens").insert_one(doc)
    return doc


def consume_password_reset_token(token: str) -> dict | None:
    now = utc_now()
    return get_collection("password_reset_tokens").find_one_and_update(
        {
            "token": token,
            "used_at": None,
            "expires_at": {"$gt": now},
        },
        {"$set": {"used_at": now}},
        return_document=ReturnDocument.AFTER,
    )


def update_user_password(user_id: str | ObjectId, password_hash: str) -> bool:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    result = get_collection("users").update_one(
        {"_id": oid},
        {"$set": {"password_hash": password_hash, "updated_at": utc_now()}},
    )
    return result.modified_count == 1


def increment_usage(user_id: str | ObjectId, feature: str, limit: int, window_seconds: int = 86_400) -> dict:
    oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    now = utc_now()

    window_start_ts = int(now.timestamp() // window_seconds) * window_seconds
    window_start = datetime.fromtimestamp(window_start_ts, tz=timezone.utc)

    counter = get_collection("usage_counters").find_one_and_update(
        {
            "user_id": oid,
            "feature": feature,
            "window_start": window_start,
        },
        {
            "$inc": {"count": 1},
            "$setOnInsert": {
                "created_at": now,
                "expires_at": window_start + timedelta(seconds=window_seconds),
            },
            "$set": {"updated_at": now},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    if counter is None:
        return {
            "allowed": False,
            "used": 0,
            "limit": limit,
            "remaining": limit,
            "window_start": window_start,
        }

    used = int(counter.get("count", 0))
    allowed = used <= limit
    remaining = max(limit - used, 0)

    return {
        "allowed": allowed,
        "used": used,
        "limit": limit,
        "remaining": remaining,
        "window_start": _ensure_utc(counter["window_start"]),
    }


def record_login_attempt(email: str, success: bool, window_minutes: int = 15) -> dict:
    email_key = email.strip().lower()
    now = utc_now()
    window_seconds = window_minutes * 60
    window_start_ts = int(now.timestamp() // window_seconds) * window_seconds
    window_start = datetime.fromtimestamp(window_start_ts, tz=timezone.utc)

    doc = get_collection("auth_attempts").find_one_and_update(
        {"email": email_key, "window_start": window_start},
        {
            "$inc": {
                "attempts": 1,
                "failures": 0 if success else 1,
            },
            "$setOnInsert": {
                "created_at": now,
                "expires_at": window_start + timedelta(minutes=window_minutes),
            },
            "$set": {"updated_at": now},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    if doc is None:
        return {
            "attempts": 0,
            "failures": 0,
            "window_start": window_start,
        }

    return {
        "attempts": int(doc.get("attempts", 0)),
        "failures": int(doc.get("failures", 0)),
        "window_start": _ensure_utc(doc["window_start"]),
    }


def get_login_attempt_window(email: str, window_minutes: int = 15) -> dict:
    email_key = email.strip().lower()
    now = utc_now()
    window_seconds = window_minutes * 60
    window_start_ts = int(now.timestamp() // window_seconds) * window_seconds
    window_start = datetime.fromtimestamp(window_start_ts, tz=timezone.utc)

    doc = get_collection("auth_attempts").find_one({"email": email_key, "window_start": window_start})
    if not doc:
        return {
            "attempts": 0,
            "failures": 0,
            "window_start": window_start,
        }

    return {
        "attempts": int(doc.get("attempts", 0)),
        "failures": int(doc.get("failures", 0)),
        "window_start": _ensure_utc(doc["window_start"]),
    }
