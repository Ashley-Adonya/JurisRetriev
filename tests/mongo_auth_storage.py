from models.mongodb import init_indexes
from models.auth_service import authenticate, consume_quota, register_user, verify_email


if __name__ == "__main__":
    init_indexes()

    # 1) Inscription
    reg = register_user("demo.user@example.com", "StrongPassword!123")
    print("REGISTER:", reg)

    # 2) Auth avant vérification email
    pre_auth = authenticate("demo.user@example.com", "StrongPassword!123")
    print("AUTH BEFORE VERIFY:", pre_auth)

    # 3) Vérification email
    verified = verify_email(reg["verification_token"])
    print("EMAIL VERIFIED:", verified)

    # 4) Auth après vérification email
    post_auth = authenticate("demo.user@example.com", "StrongPassword!123")
    print("AUTH AFTER VERIFY:", post_auth)

    # 5) Quota / usage
    if post_auth.get("ok"):
        quota = consume_quota(post_auth["user_id"], feature="rag_request", limit=3)
        print("QUOTA:", quota)
