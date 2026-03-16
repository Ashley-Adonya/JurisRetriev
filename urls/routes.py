from flask import Blueprint, jsonify

from views.auth_views import (
    auth_register_view,
    auth_verify_email_view,
    auth_login_view,
    auth_logout_view,
    auth_me_view,
    auth_forgot_password_view,
    auth_reset_password_view,
    auth_resend_verification_view,
)
from views.rag_views import rag_upsert_documents_view, rag_query_view, rag_history_view, rag_conversations_view
from views.admin_views import admin_stats_view

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.get("/health")
def health():
    return jsonify({"ok": True})

api_bp.post("/auth/register")(auth_register_view)
api_bp.post("/auth/verify-email")(auth_verify_email_view)
api_bp.post("/auth/login")(auth_login_view)
api_bp.post("/auth/logout")(auth_logout_view)
api_bp.get("/auth/me")(auth_me_view)
api_bp.post("/auth/forgot-password")(auth_forgot_password_view)
api_bp.post("/auth/reset-password")(auth_reset_password_view)
api_bp.post("/auth/resend-verification")(auth_resend_verification_view)

api_bp.post("/rag/documents")(rag_upsert_documents_view)
api_bp.post("/rag/query")(rag_query_view)
api_bp.get("/rag/history")(rag_history_view)
api_bp.get("/rag/conversations")(rag_conversations_view)

# Admin
api_bp.get("/admin/stats")(admin_stats_view)

def register_routes(app):
    app.register_blueprint(api_bp)
