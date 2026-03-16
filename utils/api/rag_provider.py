import requests
import numpy as np
import os
import dotenv
from .store_vector import store_vector_in_json, load_vectors_from_json, clear_vectors_cache
from models.rag_store import upsert_rag_document, load_rag_documents



"""

The principe is quite simple, 
- you take a large piece of texts(your knowledge base) and you chunk it (the way matter).
- for each part of your knowledge base you calculate using an embedding model the vector representation
- and last but not least for any given query you calculate the same representation to compare them using cosine_similarity.




TODO: Implement Reranking to improve perf.


"""

def cosine_similarity(vect1, vect2):
	vect1 = np.array(vect1) # (n, n_embds)
	vect2 = np.array(vect2) # (n_embds,)
	eps = np.finfo(float).eps  # petit epsilon pour éviter la division par zéro
	norm = np.linalg.norm(vect1, axis=-1) * np.linalg.norm(vect2)  # (n,)
	return np.dot(vect1, vect2) / np.maximum(norm, eps)  # (n,)


def embedding_model_api(input):
	dotenv.load_dotenv()
	# Here we will use Jina api for embeddings(it would be the same as if we were running localy a small embeds model
	api_key = os.getenv('JINA_API_KEY')
	model = os.getenv("JINA_MODEL")
	
	
	try:
		response = requests.post(
			"https://api.jina.ai/v1/embeddings",
			headers={
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
			},
			json={
				"model": model,
				"task": "retrieval.passage",
				"normalized": True,
				"input": input  # for them input is a list of string
			},
			timeout=30
		)
		
		if response.status_code == 200:
			return list(map(lambda x: x["embedding"],response.json()["data"]))
		else:
			print(f"[ERROR API] Status: {response.status_code}")
			print(f"[ERROR API] Response: {response.text[:200]}")
			return []  # In this error case we will just return an empty list.
	except Exception as e:
		print(f"[ERROR Exception] {e}")
		return []

def doc_to_vect(doc):
	"""Génère un embedding pour un document entier."""
	# Plutôt que de splitter par ligne et faire des appels API séparés,
	# on traite le document comme un tout
	return embedding_model_api([doc["doc_text"]])

def build_knowledgebase(docs, use_cache=True):
	"""Construit la knowledge base avec les embeddings des documents.
	
	Args:
		docs: Liste des documents avec 'doc_info' et 'doc_text'
		use_cache: Si True, essaie de charger depuis le cache. Si False, recrée les embeddings.
	"""
	# Essayer de charger depuis le cache si demandé
	if use_cache:
		cached = load_vectors_from_json()
		if cached:
			if not docs:
				docs = load_rag_documents()
			knowledgebase = {
				"docs": [],
				"embeddings": []
			}
			end = 0
			for item in cached:
				start = end
				embedding = item["embedding"]
				end = start + 1
				knowledgebase["docs"].append({
					"doc_info": item["doc_info"],
					"embeds_range": (start, end)
				})
				if isinstance(embedding, np.ndarray):
					knowledgebase["embeddings"].append(embedding.tolist())
				else:
					knowledgebase["embeddings"].append(embedding)
			return knowledgebase
	
	# Sinon, créer les embeddings
	knowledgebase = {
		"docs": [],
		"embeddings": []
	}

	end = 0
	for i in range(0, len(docs)):
		embeds = doc_to_vect(docs[i])
		upsert_rag_document(docs[i]["doc_info"], docs[i]["doc_text"])
		start = end
		end = start + len(embeds)
		knowledgebase["docs"].append({"doc_info": docs[i]["doc_info"],
		"embeds_range": (start, end)
		})
		knowledgebase["embeddings"].extend(embeds)
		
		# Sauvegarder chaque embedding dans le cache
		for embed in embeds:
			store_vector_in_json(np.array(embed), docs[i]["doc_info"])
	
	return knowledgebase


def find_relevant_docs(docs, topk_id):
	"""Recherche le document contenant l'embedding à l'indice topk_id."""
	if not docs or len(docs) == 0:
		return None, None
	
	mid = len(docs) // 2
	
	# Vérifier que l'indice mid existe et que embeds_range est valide
	if "embeds_range" not in docs[mid]:
		return None, None
	
	doc_start, doc_end = docs[mid]["embeds_range"]
	
	if doc_end <= topk_id:
		# L'indice est après ce document
		if mid + 1 < len(docs):
			return find_relevant_docs(docs[mid+1:], topk_id)
		return None, None
	elif doc_start > topk_id:
		# L'indice est avant ce document
		if mid > 0:
			return find_relevant_docs(docs[:mid], topk_id)
		return None, None
	else:
		# L'indice est dans ce document
		return docs[mid], topk_id - doc_start

def retrieve_relevant_doc(query, knowledgebase, topk=3):
	"""Récupère les documents les plus pertinents pour une requête."""
	# Vérifier que la knowledge base n'est pas vide
	if not knowledgebase.get("embeddings") or len(knowledgebase["embeddings"]) == 0:
		return []  # knowledge base vide
	
	try:
		query_embds = embedding_model_api([query])  # on passe une liste, pas une string
		if not query_embds:
			return []  # erreur API
		
		query_vec = np.array(query_embds[0])         # vecteur de la requête : (n_embds,)
		
		# Convertir les embeddings : gérer les cas où c'est une liste de listes
		embeddings_list = knowledgebase["embeddings"]
		if embeddings_list and isinstance(embeddings_list[0], list):
			kb_embeds = np.array(embeddings_list)  # (m, n_embds)
		else:
			kb_embeds = np.array(embeddings_list)  # conversion directe
		
		# Gérer le cas d'un vecteur seul (reshape si nécessaire)
		if kb_embeds.ndim == 1:
			kb_embeds = kb_embeds.reshape(1, -1)
		
		scores = cosine_similarity(kb_embeds, query_vec)   # (m,)
		topk_ids = np.argsort(-scores)[:topk]  # -scores car numpy trie par ordre croissant
		
		# Récupérer les documents
		results = []
		for idx in topk_ids:
			doc, offset = find_relevant_docs(knowledgebase["docs"], int(idx))
			if doc is not None:
				results.append({"doc": doc, "score": float(scores[idx]), "offset": int(offset) if offset is not None else None})
		
		return results
		
	except Exception as e:
		print(f"[ERREUR] retrieve_relevant_doc: {e}")
		import traceback
		traceback.print_exc()
		return []


def reset_knowledgebase():
	"""Réinitialise la knowledge base en effaçant le cache."""
	clear_vectors_cache()