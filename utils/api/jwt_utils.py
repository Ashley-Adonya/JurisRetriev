import jwt
import datetime
from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv
from models import auth_store

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("CRITICAL: La variable d'environnement JWT_SECRET n'est pas définie !")

JWT_COOKIE_NAME = os.getenv("JWT_COOKIE_NAME", "jr_session")
JWT_TTL_DAYS = int(os.getenv("JWT_TTL_DAYS", "7"))

def encode_jwt(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=JWT_TTL_DAYS),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _use_secure_cookie() -> bool:
    secure_env = (os.getenv("COOKIE_SECURE") or "").strip().lower()
    if secure_env in {"1", "true", "yes", "on"}:
        return True
    if secure_env in {"0", "false", "no", "off"}:
        return False
    return (os.getenv("FLASK_ENV") or "").strip().lower() == "production"


def set_auth_cookie(response, token: str):
    response.set_cookie(
        JWT_COOKIE_NAME,
        token,
        max_age=JWT_TTL_DAYS * 24 * 3600,
        httponly=True,
        secure=_use_secure_cookie(),
        samesite="Lax",
        path="/",
    )
    return response


def clear_auth_cookie(response):
    response.set_cookie(
        JWT_COOKIE_NAME,
        "",
        expires=0,
        max_age=0,
        httponly=True,
        secure=_use_secure_cookie(),
        samesite="Lax",
        path="/",
    )
    return response


def _token_from_request() -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        if token and token.lower() != "null":
            return token

    cookie_token = request.cookies.get(JWT_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    return None


def get_request_user() -> dict | None:
    token = _token_from_request()
    if not token:
        return None

    decoded = decode_jwt(token)
    if not decoded:
        return None

    user_id = decoded.get("user_id")
    token_email = (decoded.get("email") or "").strip().lower()
    if not user_id or not token_email:
        return None

    try:
        user = auth_store.find_user_by_id(user_id)
    except Exception:
        return None
    if not user:
        return None

    db_email = (user.get("email") or "").strip().lower()
    if db_email != token_email:
        return None
    if not user.get("email_verified", False):
        return None
    if not user.get("is_active", True):
        return None

    return {
        "user_id": str(user.get("_id")),
        "email": db_email,
    }


def is_admin_user(user: dict | None) -> bool:
    if not user:
        return False
    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    if not admin_email:
        return False
    return (user.get("email") or "").strip().lower() == admin_email

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resolved_user = get_request_user()
        if not resolved_user:
            return jsonify({"ok": False, "error": "missing_or_invalid_authorization_header"}), 401

        request.user = resolved_user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resolved_user = get_request_user()
        if not resolved_user:
            return jsonify({"ok": False, "error": "missing_or_invalid_authorization_header"}), 401
        if not is_admin_user(resolved_user):
            return jsonify({"ok": False, "error": "unauthorized", "message": "Accès Administrateur requis."}), 403

        request.user = resolved_user
        return f(*args, **kwargs)
    return decorated
