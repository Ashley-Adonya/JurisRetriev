import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_welcome_email(to_email: str, verification_url: str):
    """
    Envoie un email de bienvenue et d'avertissement.
    Utilise le serveur SMTP configuré dans le .env ou simule l'envoi s'il n'est pas configuré.
    """
    subject = "Bienvenue sur JurisRetriev - Important"
    body = f"""Bonjour,

Bienvenue sur JurisRetriev ! 

Veuillez confirmer votre adresse email en cliquant sur ce lien :
{verification_url}

Veuillez noter que ce projet est actuellement une expérience technique et non un produit fini.
Les modèles de langages (LLM) utilisés pour formuler les réponses peuvent être sujets à des "hallucinations" ou erreurs d'interprétation juridique. Il faut rester vigilant et toujours vérifier les sources citées.

L'équipe JurisRetriev.
"""

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "noreply@jurisretriev.com")

    if smtp_server and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"Email envoyé avec succès via SMTP à {to_email}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'email via SMTP : {e}")
            return False
    else:
        # Simulation d'envoi stricte en local (fallback)
        logging.warning("=== SIMULATION ENVOI EMAIL (Aucun SMTP configuré) ===")
        logging.warning(f"TO: {to_email}\nSUBJECT: {subject}\nBODY:\n{body}")
        logging.warning("=====================================================")
        return True


def send_email_verification_email(to_email: str, verification_url: str):
    subject = "JurisRetriev - Vérification de votre email"
    body = f"""Bonjour,

Pour activer votre compte, veuillez confirmer votre adresse email en cliquant sur ce lien :
{verification_url}

Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.

L'équipe JurisRetriev.
"""

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "noreply@jurisretriev.com")

    if smtp_server and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"Email de vérification envoyé avec succès via SMTP à {to_email}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'email de vérification via SMTP : {e}")
            return False
    else:
        logging.warning("=== SIMULATION ENVOI EMAIL VERIFICATION (Aucun SMTP configuré) ===")
        logging.warning(f"TO: {to_email}\nSUBJECT: {subject}\nBODY:\n{body}")
        logging.warning("==============================================================")
        return True


def send_password_reset_email(to_email: str, reset_url: str):
    subject = "JurisRetriev - Réinitialisation de votre mot de passe"
    body = f"""Bonjour,

Vous avez demandé une réinitialisation de mot de passe.

Cliquez sur ce lien pour définir un nouveau mot de passe :
{reset_url}

Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.

L'équipe JurisRetriev.
"""

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "noreply@jurisretriev.com")

    if smtp_server and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            logging.info(f"Email de reset envoyé avec succès via SMTP à {to_email}")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'email de reset via SMTP : {e}")
            return False

    logging.warning("=== SIMULATION ENVOI EMAIL RESET (Aucun SMTP configuré) ===")
    logging.warning(f"TO: {to_email}\nSUBJECT: {subject}\nBODY:\n{body}")
    logging.warning("============================================================")
    return True
