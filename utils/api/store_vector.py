import numpy as np
from models.rag_store import clear_rag_storage, load_rag_vectors, upsert_rag_vector


def store_vector_in_json(vector: np.ndarray, doc_info: str):
    """Compatibilité: stocke désormais le vecteur dans MongoDB (collection rag_vectors)."""
    upsert_rag_vector(doc_info, vector.tolist())


def load_vectors_from_json():
    """Compatibilité: charge désormais les vecteurs depuis MongoDB."""
    data = load_rag_vectors()
    return [{"embedding": np.array(doc["embedding"]), "doc_info": doc["doc_info"]} for doc in data]


def clear_vectors_cache():
    """Compatibilité: vide le stockage MongoDB des docs et vecteurs RAG."""
    clear_rag_storage()

            
            



