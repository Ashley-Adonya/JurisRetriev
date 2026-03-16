import os
from flask import Flask, render_template, redirect, url_for, request
from flask_cors import CORS
from models.mongodb import init_indexes
from urls.routes import register_routes
from models.auth_service import register_user, verify_email
from utils.api.jwt_utils import get_request_user, is_admin_user

app = Flask(__name__)
# Active CORS pour faciliter les appels JS (depuis le front Tailwind)
CORS(app)

# Initialisation des index MongoDB
init_indexes()

# Initialisation de l'administrateur depuis les variables d'environnement
admin_email = os.getenv("ADMIN_EMAIL")
admin_pass = os.getenv("ADMIN_PASSWORD")
if admin_email and admin_pass:
    try:
        register_user(admin_email, admin_pass)
        print(f"✅ Compte administrateur vérifié/créé : {admin_email}")
    except ValueError as exc:
        if str(exc) != "email déjà utilisé":
            print(f"⚠️ Initialisation admin ignorée: {exc}")

# Routage des vues d'API
register_routes(app)

@app.route("/")
def serve_landing():
    return render_template("landing.html")

@app.route("/chat")
def serve_chat():
    user = get_request_user()
    if not user:
        return redirect(url_for("serve_login", reason="auth_required", next="/chat"))
    return render_template("chat.html")

@app.route("/admin")
def serve_admin():
    user = get_request_user()
    if not user or not is_admin_user(user):
        return redirect(url_for("serve_login", reason="admin_required", next="/admin"))
    return render_template("admin.html")

@app.route("/login")
def serve_login():
    reason = (request.args.get("reason") or "").strip()
    next_path = (request.args.get("next") or "/chat").strip()

    reason_messages = {
        "auth_required": "Vous devez vous connecter pour accéder à cette page.",
        "admin_required": "Cette section est réservée aux administrateurs.",
        "session_expired": "Votre session a expiré. Veuillez vous reconnecter.",
        "logged_out": "Vous avez été déconnecté avec succès.",
    }

    message = reason_messages.get(reason, "Connectez-vous pour continuer.")
    return render_template("login.html", reason=reason, message=message, next_path=next_path)


@app.route("/forgot-password")
def serve_forgot_password():
    return render_template("forgot_password.html")


@app.route("/reset-password")
def serve_reset_password():
    token = (request.args.get("token") or "").strip()
    if not token:
        return render_template(
            "reset_password.html",
            token="",
            token_valid=False,
            message="Lien invalide : token manquant.",
        ), 400
    return render_template(
        "reset_password.html",
        token=token,
        token_valid=True,
        message="",
    )


@app.route("/verify-email")
def serve_verify_email():
    token = (request.args.get("token") or "").strip()
    if not token:
        return render_template(
            "verify_email.html",
            ok=False,
            message="Lien de vérification invalide : token manquant.",
        ), 400

    ok = verify_email(token)
    if not ok:
        return render_template(
            "verify_email.html",
            ok=False,
            message="Lien invalide ou expiré. Veuillez vous réinscrire pour recevoir un nouveau lien.",
        ), 400

    return render_template(
        "verify_email.html",
        ok=True,
        message="Votre adresse email a bien été vérifiée. Vous pouvez maintenant vous connecter.",
    )

@app.route("/contact")
def serve_contact():
    admin_email = os.getenv("ADMIN_EMAIL", "admin@jurisretriev.com")
    return render_template("contact.html", admin_email=admin_email)

@app.route("/about")
def serve_about():
    return render_template("about.html")

@app.route("/<path:path>")
def catch_all(path):
    if path.startswith("api/"):
        return {"ok": False, "error": "not_found"}, 404
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
