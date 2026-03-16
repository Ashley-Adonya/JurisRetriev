from flask import jsonify, request
from models.auth_service import consume_quota
from models.rag_store import load_rag_documents, upsert_rag_document
from models.mongodb import get_collection, utc_now
from utils.api.augmented_gen import answer_with_augmented_rag
from utils.api.jwt_utils import jwt_required, admin_required
from utils.api.llm_provider import generate_response_openai, initialize_context

@admin_required
def rag_upsert_documents_view():
    payload = request.get_json(silent=True) or {}
    docs = payload.get("docs") or []

    if not isinstance(docs, list) or not docs:
        return jsonify({"ok": False, "error": "docs_list_required"}), 400

    count = 0
    for doc in docs:
        doc_info = (doc.get("doc_info") or "").strip()
        doc_text = doc.get("doc_text") or ""
        if not doc_info or not doc_text:
            continue
        
        # 1. Reformuler document avec LLM avant sauvegarde en BDD (Demande utilisateur)
        reformated_text = _reformulate_temp_doc(doc_text)
        
        # 2. Sauvegarder dans MongoDB (rag_store s'occupera plus tard de créer l'embedding via rag_provider)
        upsert_rag_document(doc_info, reformated_text)
        count += 1

    return jsonify({"ok": True, "stored": count, "message": "Documents formatés par LLM et indexés"}), 200

def _reformulate_temp_doc(doc_text: str) -> str:
    system_prompt = "Tu es un expert juridique. Reformule le texte suivant de manière structurée et concise pour qu'il soit utilisé comme contexte dans un système RAG."
    context = initialize_context(system_prompt, doc_text[:10000]) # Roughly limit to 4 pages (10k chars)
    return generate_response_openai(context, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions")


def _load_conversation_context(user_id: str, conversation_id: str | None, limit: int = 6) -> str:
    if not conversation_id:
        return ""

    history_coll = get_collection("chat_history")
    cursor = history_coll.find(
        {"user_id": user_id, "conversation_id": conversation_id}
    ).sort("created_at", -1).limit(limit)

    turns = list(cursor)
    if not turns:
        return ""

    turns.reverse()
    blocks: list[str] = []
    for item in turns:
        q = (item.get("query") or "").strip()
        a = (item.get("answer") or "").strip()
        if q:
            blocks.append(f"Utilisateur: {q}")
        if a:
            blocks.append(f"Assistant: {a[:1200]}")

    return "\n".join(blocks)


def _parse_positive_int(value: str | None, default: int, min_v: int = 1, max_v: int = 100) -> int:
    try:
        parsed = int(value or default)
    except Exception:
        parsed = default
    return max(min_v, min(max_v, parsed))

@jwt_required
def rag_query_view():
    payload = request.get_json(silent=True) or {}
    user_id = getattr(request, "user", {}).get("user_id")
    query = payload.get("query") or ""
    mode = payload.get("mode") or "defense_expert"
    topk = int(payload.get("topk", 3))
    temp_docs = payload.get("temp_docs") or []
    conversation_id = payload.get("conversation_id") or None

    if not user_id or not query:
        return jsonify({"ok": False, "error": "user_id_and_query_required"}), 400

    quota = consume_quota(user_id=user_id, feature="rag_query", limit=5, window_seconds=86400)
    if not quota["allowed"]:
        return jsonify({
            "ok": False, 
            "error": "quota_exceeded", 
            "contact": "Ashley Sado (ashleysado17@gmail.com)",
            "message": "Quota dépassé. Veuillez contacter Ashley Sado pour augmenter votre limite.",
            "quota": quota
        }), 429

    docs = load_rag_documents() or []
    
    # Process temporary docs without saving
    processed_temp_docs = []
    for t_doc in temp_docs:
        doc_info = t_doc.get("doc_info", "User_Doc")
        doc_text = t_doc.get("doc_text", "")
        if doc_text:
            reformulated = _reformulate_temp_doc(doc_text)
            processed_temp_docs.append({
                "doc_info": f"[TEMP] {doc_info}",
                "doc_text": reformulated
            })
    
    all_docs = docs + processed_temp_docs

    if not all_docs:
        return jsonify({"ok": False, "error": "no_documents"}), 400

    conversation_context = _load_conversation_context(user_id=user_id, conversation_id=conversation_id, limit=6)

    result = answer_with_augmented_rag(
        query=query,
        docs=all_docs,
        mode=mode,
        topk=topk,
        use_cache=True,
        reformulate=True,
        conversation_context=conversation_context,
    )

    # Sauvegarde dans l'historique de chat
    history_coll = get_collection("chat_history")
    history_coll.insert_one({
        "user_id": user_id,
        "created_at": utc_now(),
        "query": query,
        "mode": mode,
        "conversation_id": conversation_id,
        "temp_docs": temp_docs,
        "answer": result.get("answer"),
        "retrieved": result.get("retrieved", []),
        "rewritten_query": result.get("rewritten_query"),
    })

    return jsonify({"ok": True, "quota": quota, **result})


@jwt_required
def rag_history_view():
    user_id = getattr(request, "user", {}).get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "user_not_found"}), 400

    conversation_id = (request.args.get("conversation_id") or "").strip()
    limit = _parse_positive_int(request.args.get("limit"), default=50 if conversation_id else 20)

    history_coll = get_collection("chat_history")
    query_filter: dict = {"user_id": user_id}
    if conversation_id:
        query_filter["conversation_id"] = conversation_id

    cursor = history_coll.find(query_filter).sort("created_at", -1).limit(limit)

    items: list[dict] = []
    for doc in cursor:
        items.append({
            "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
            "query": doc.get("query"),
            "mode": doc.get("mode"),
            "conversation_id": doc.get("conversation_id"),
            "temp_docs": doc.get("temp_docs", []),
            "answer": doc.get("answer"),
            "rewritten_query": doc.get("rewritten_query"),
        })

    return jsonify({"ok": True, "items": items})


@jwt_required
def rag_conversations_view():
    user_id = getattr(request, "user", {}).get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "user_not_found"}), 400

    limit = _parse_positive_int(request.args.get("limit"), default=30, max_v=100)

    history_coll = get_collection("chat_history")
    pipeline = [
        {"$match": {"user_id": user_id, "conversation_id": {"$ne": None}}},
        {"$sort": {"created_at": -1}},
        {
            "$group": {
                "_id": "$conversation_id",
                "last_created_at": {"$first": "$created_at"},
                "last_query": {"$first": "$query"},
                "last_mode": {"$first": "$mode"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"last_created_at": -1}},
        {"$limit": limit},
    ]

    rows = list(history_coll.aggregate(pipeline))
    items: list[dict] = []
    for row in rows:
        conv_id = row.get("_id")
        if not conv_id:
            continue
        last_query = (row.get("last_query") or "").strip()
        items.append(
            {
                "conversation_id": conv_id,
                "title": (last_query[:80] + "…") if len(last_query) > 80 else (last_query or "Conversation"),
                "last_query": last_query,
                "last_mode": row.get("last_mode") or "defense_expert",
                "count": int(row.get("count") or 0),
                "last_created_at": row.get("last_created_at").isoformat() if row.get("last_created_at") else None,
            }
        )

    return jsonify({"ok": True, "items": items})
