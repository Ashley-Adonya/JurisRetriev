#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jeff/Bureau/justForFun/JurisRetriev')

from utils.api.rag_provider import embedding_model_api
import numpy as np

# Test simple
test_text = "Article 1 : Les lois sont exécutoires"
print(f"Test avec texte: {test_text[:50]}...")

result = embedding_model_api([test_text])
print(f"Résultat API: type={type(result)}, len={len(result) if result else 0}")

if result:
    print(f"Premier élément: type={type(result[0])}, len={len(result[0]) if hasattr(result[0], '__len__') else 'N/A'}")
    if isinstance(result[0], list):
        print(f"C'est une liste avec {len(result[0])} éléments")
    elif isinstance(result[0], (int, float)):
        print(f"C'est un nombre: {result[0]}")
