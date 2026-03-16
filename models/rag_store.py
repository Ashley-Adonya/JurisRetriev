from __future__ import annotations

from typing import Any

from .mongodb import get_collection, utc_now


def upsert_rag_document(doc_info: str, doc_text: str) -> None:
    now = utc_now()
    get_collection("rag_documents").update_one(
        {"doc_info": doc_info},
        {
            "$set": {
                "doc_info": doc_info,
                "doc_text": doc_text,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def upsert_rag_vector(doc_info: str, vector: list[float]) -> None:
    now = utc_now()
    get_collection("rag_vectors").update_one(
        {"doc_info": doc_info},
        {
            "$set": {
                "doc_info": doc_info,
                "vector": vector,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )


def load_rag_vectors() -> list[dict[str, Any]]:
    rows = list(get_collection("rag_vectors").find({}, {"_id": 0, "doc_info": 1, "vector": 1}).sort("doc_info", 1))
    return [{"doc_info": r["doc_info"], "embedding": r["vector"]} for r in rows]


def load_rag_documents() -> list[dict[str, str]]:
    rows = list(get_collection("rag_documents").find({}, {"_id": 0, "doc_info": 1, "doc_text": 1}).sort("doc_info", 1))
    return [{"doc_info": r["doc_info"], "doc_text": r["doc_text"]} for r in rows]


def clear_rag_storage() -> None:
    get_collection("rag_vectors").delete_many({})
    get_collection("rag_documents").delete_many({})
