from utils.api.augmented_gen import answer_with_augmented_rag


DOCS = [
    {
        "doc_info": "code_penal",
        "doc_text": "Article 311-1: Le vol est la soustraction frauduleuse de la chose d'autrui.\n"
        "Article 313-1: L'escroquerie est le fait, soit par l'usage d'un faux nom...",
    },
    {
        "doc_info": "code_civil",
        "doc_text": "Article 1240: Tout fait quelconque de l'homme, qui cause à autrui un dommage, "
        "oblige celui par la faute duquel il est arrivé à le réparer.",
    },
    {
        "doc_info": "procedure_penale",
        "doc_text": "Le dépôt de plainte peut être effectué auprès d'un commissariat, d'une gendarmerie "
        "ou du procureur de la République.",
    },
]


if __name__ == "__main__":
    query = "Mon ami a pris mon ticket gagnant en mentant, que faire ?"

    result = answer_with_augmented_rag(
        query=query,
        docs=DOCS,
        mode="defense_expert",
        topk=3,
        use_cache=False,
        reformulate=True,
    )

    print("\n=== MODE ===")
    print(result["mode"])

    print("\n=== QUERY REFORMULÉE ===")
    print(result["rewritten_query"])

    print("\n=== SOURCES RETROUVÉES ===")
    for i, item in enumerate(result["retrieved"], 1):
        print(f"{i}. {item['doc']['doc_info']} (score={item['score']:.4f})")

    print("\n=== RÉPONSE ===")
    print(result["answer"])
