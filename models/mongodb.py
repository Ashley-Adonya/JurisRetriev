from __future__ import annotations

import os
from datetime import datetime, timezone

import dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


dotenv.load_dotenv()

_CLIENT: MongoClient | None = None
_DB: Database | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _mongo_uri() -> str:
    return os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")


def _mongo_db_name() -> str:
    return os.getenv("MONGODB_DB", "jurisretriev")


def connect_db() -> Database:
    global _CLIENT, _DB
    if _DB is None:
        _CLIENT = MongoClient(_mongo_uri())
        _DB = _CLIENT[_mongo_db_name()]
    return _DB


def close_db() -> None:
    global _CLIENT, _DB
    if _CLIENT is not None:
        _CLIENT.close()
    _CLIENT = None
    _DB = None


def get_collection(name: str) -> Collection:
    return connect_db()[name]


def init_indexes() -> None:
    db = connect_db()

    users = db["users"]
    users.create_index([("email", ASCENDING)], unique=True, name="uniq_user_email")

    verification_tokens = db["email_verification_tokens"]
    verification_tokens.create_index([("token", ASCENDING)], unique=True, name="uniq_verification_token")
    verification_tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_verification_token")
    verification_tokens.create_index([("user_id", ASCENDING)], name="idx_verification_user")

    password_reset_tokens = db["password_reset_tokens"]
    password_reset_tokens.create_index([("token", ASCENDING)], unique=True, name="uniq_password_reset_token")
    password_reset_tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_password_reset_token")
    password_reset_tokens.create_index([("user_id", ASCENDING)], name="idx_password_reset_user")

    usage = db["usage_counters"]
    usage.create_index(
        [("user_id", ASCENDING), ("feature", ASCENDING), ("window_start", ASCENDING)],
        unique=True,
        name="uniq_usage_counter",
    )

    auth_attempts = db["auth_attempts"]
    auth_attempts.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_auth_attempts")
    auth_attempts.create_index([("email", ASCENDING), ("window_start", ASCENDING)], name="idx_auth_attempts")

    rag_documents = db["rag_documents"]
    rag_documents.create_index([("doc_info", ASCENDING)], unique=True, name="uniq_rag_doc_info")

    rag_vectors = db["rag_vectors"]
    rag_vectors.create_index([("doc_info", ASCENDING)], unique=True, name="uniq_rag_vector_doc_info")

    chat_history = db["chat_history"]
    chat_history.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)], name="idx_chat_history_user_date")
    chat_history.create_index([("conversation_id", ASCENDING)], name="idx_chat_history_conv")

    chat_history = db["chat_history"]
    chat_history.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)], name="idx_chat_history_user_date")


__all__ = ["connect_db", "close_db", "get_collection", "init_indexes", "utc_now"]
