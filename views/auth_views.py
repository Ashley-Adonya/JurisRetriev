from flask import jsonify, request
from urllib.parse import quote
import os
from models.auth_service import (
    register_user,
    verify_email,
    authenticate,
    request_password_reset,
    reset_password_with_token,
    request_email_verification_resend,
)
from utils.api.jwt_utils import encode_jwt, set_auth_cookie, clear_auth_cookie, get_request_user, is_admin_user
from utils.api.email_service import send_welcome_email, send_password_reset_email, send_email_verification_email

def auth_register_view():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "error": "email_and_password_required"}), 400

    try:
        result = register_user(email, password)
        # Envoi de l'email d'avertissement LLM
        token = result.get("verification_token", "")
        app_base_url = (os.getenv("APP_BASE_URL") or "http://localhost:5000").rstrip("/")
        verification_url = f"{app_base_url}/verify-email?token={quote(token)}"
        send_welcome_email(email, verification_url)

        # Ne pas exposer le token de vérification au client HTTP
        return jsonify({
            "ok": True,
            "user_id": result.get("user_id"),
            "email": result.get("email"),
            "email_verified": False,
        }), 201
    except ValueError as exc:
        error_message = str(exc)
        status = 409 if error_message == "email déjà utilisé" else 400
        return jsonify({"ok": False, "error": error_message, "message": error_message}), status

def auth_verify_email_view():
    payload = request.get_json(silent=True) or {}
    token = payload.get("token") or ""

    if not token:
        return jsonify({"ok": False, "error": "token_required"}), 400

    ok = verify_email(token)
    if not ok:
        return jsonify({"ok": False, "error": "invalid_or_expired_token"}), 400

    return jsonify({"ok": True})

def auth_login_view():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "error": "email_and_password_required"}), 400

    result = authenticate(email, password)
    if not result.get("ok"):
        status = 429 if result.get("reason") == "too_many_attempts" else 401
        return jsonify(result), status

    # Generate JWT
    user_id = str(result.get("user_id"))
    canonical_email = (result.get("email") or email).strip().lower()
    token = encode_jwt(user_id=user_id, email=canonical_email)

    is_admin = (canonical_email == (os.getenv("ADMIN_EMAIL") or "").lower())

    response = jsonify({"ok": True, "email": canonical_email, "user_id": user_id, "is_admin": is_admin})
    set_auth_cookie(response, token)
    return response


def auth_logout_view():
    response = jsonify({"ok": True})
    clear_auth_cookie(response)
    return response


def auth_me_view():
    user = get_request_user()
    if not user:
        return jsonify({"ok": False, "error": "unauthenticated"}), 401

    return jsonify({
        "ok": True,
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "is_admin": is_admin_user(user),
    })


def auth_forgot_password_view():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()

    if not email:
        return jsonify({"ok": False, "error": "email_required"}), 400

    result = request_password_reset(email)
    if result.get("sent"):
        token = result.get("token") or ""
        destination_email = (result.get("email") or email).strip().lower()
        app_base_url = (os.getenv("APP_BASE_URL") or "http://localhost:5000").rstrip("/")
        reset_url = f"{app_base_url}/reset-password?token={quote(token)}"
        send_password_reset_email(destination_email, reset_url)

    # Réponse volontairement neutre (anti-enumération)
    return jsonify({
        "ok": True,
        "message": "Si un compte existe pour cet email, un lien de réinitialisation a été envoyé.",
    })


def auth_reset_password_view():
    payload = request.get_json(silent=True) or {}
    token = (payload.get("token") or "").strip()
    password = payload.get("password") or ""

    if not token or not password:
        return jsonify({"ok": False, "error": "token_and_password_required"}), 400

    result = reset_password_with_token(token=token, new_password=password)
    if not result.get("ok"):
        return jsonify({
            "ok": False,
            "error": result.get("reason") or "reset_failed",
            "message": result.get("message") or "Réinitialisation impossible.",
        }), 400

    return jsonify({"ok": True, "message": "Mot de passe réinitialisé avec succès."})


def auth_resend_verification_view():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    if not email:
        return jsonify({"ok": False, "error": "email_required"}), 400

    result = request_email_verification_resend(email)
    if result.get("sent"):
        token = result.get("token") or ""
        destination_email = (result.get("email") or email).strip().lower()
        app_base_url = (os.getenv("APP_BASE_URL") or "http://localhost:5000").rstrip("/")
        verification_url = f"{app_base_url}/verify-email?token={quote(token)}"
        send_email_verification_email(destination_email, verification_url)

    return jsonify({
        "ok": True,
        "message": "Si le compte existe et n'est pas vérifié, un nouvel email de validation a été envoyé.",
    })
