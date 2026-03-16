from typing import Any

from .llm_provider import generate_response_openai, initialize_context
from .rag_provider import build_knowledgebase, retrieve_relevant_doc
from ..web.readfile import get_system_prompt, get_query_rewrite_prompt, list_prompt_modes


DEFAULT_CHAT_MODEL = "deepseek-chat"
DEFAULT_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"


def reformulate_query(
    query: str,
    model: str = DEFAULT_CHAT_MODEL,
    url: str = DEFAULT_CHAT_URL,
) -> str:
    rewrite_system_prompt = get_query_rewrite_prompt()
    context = initialize_context(rewrite_system_prompt, query)
    rewritten = generate_response_openai(context, model, url)
    return (rewritten or query).strip()


def _build_sources_map(docs: list[dict[str, Any]]) -> dict[str, str]:
    return {doc.get("doc_info", ""): doc.get("doc_text", "") for doc in docs}


def _format_retrieved_context(retrieved: list[dict[str, Any]], docs: list[dict[str, Any]]) -> str:
    sources = _build_sources_map(docs)
    blocks: list[str] = []
    for item in retrieved:
        doc_meta = item.get("doc", {})
        doc_info = doc_meta.get("doc_info", "source_inconnue")
        score = item.get("score", 0.0)
        doc_text = sources.get(doc_info, "")
        excerpt = doc_text[:2500]
        blocks.append(
            f"[SOURCE={doc_info}]\n"
            f"[SCORE={score:.4f}]\n"
            f"{excerpt}"
        )
    return "\n\n---\n\n".join(blocks)


def answer_with_augmented_rag(
    query: str,
    docs: list[dict[str, Any]],
    mode: str = "defense_expert",
    topk: int = 3,
    use_cache: bool = True,
    reformulate: bool = True,
    conversation_context: str = "",
    model: str = DEFAULT_CHAT_MODEL,
    url: str = DEFAULT_CHAT_URL,
) -> dict[str, Any]:
    knowledgebase = build_knowledgebase(docs, use_cache=use_cache)

    rewritten_query = reformulate_query(query, model=model, url=url) if reformulate else query
    retrieved = retrieve_relevant_doc(rewritten_query, knowledgebase, topk=topk)

    retrieved_context = _format_retrieved_context(retrieved, docs)
    system_prompt = get_system_prompt(mode)

    conversation_block = f"\n\nContexte conversationnel récent:\n{conversation_context}" if conversation_context else ""

    user_prompt = (
        "Réponds à la requête utilisateur en t'appuyant d'abord sur le contexte récupéré.\n"
        "Si le contexte est insuffisant, dis-le explicitement.\n\n"
        f"Requête utilisateur: {query}\n"
        f"Requête reformulée: {rewritten_query}\n\n"
        f"Contexte récupéré:\n{retrieved_context}"
        f"{conversation_block}"
    )

    context = initialize_context(system_prompt, user_prompt)
    answer = generate_response_openai(context, model=model, url=url)

    return {
        "mode": mode,
        "available_modes": list_prompt_modes(),
        "query": query,
        "rewritten_query": rewritten_query,
        "retrieved": retrieved,
        "answer": answer,
    }
