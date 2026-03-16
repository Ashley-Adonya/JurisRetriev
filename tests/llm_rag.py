from utils.api.llm_provider import *
from utils.api.rag_provider import *

code_travail_lois = """
Article L1221-1 : Le contrat de travail est soumis aux règles du droit commun. Il peut être établi selon les formes que les parties contractantes décident d’adopter. :contentReference[oaicite:2]{index=2}

Article L1221-3 : Le contrat de travail établi par écrit est rédigé en français. Le salarié étranger peut demander une traduction du contrat dans sa langue. :contentReference[oaicite:3]{index=3}

Article L1231-1 : Le contrat de travail à durée indéterminée peut être rompu à l’initiative de l’employeur ou du salarié, ou d’un commun accord, dans les conditions prévues par les dispositions du présent titre. Ces dispositions ne sont pas applicables pendant la période d’essai. :contentReference[oaicite:4]{index=4}

Article L1231-2 : Les dispositions du présent titre ne dérogent pas aux dispositions légales assurant une protection particulière à certains salariés. :contentReference[oaicite:5]{index=5}

Article L1232-1 : Tout licenciement pour motif personnel est motivé dans les conditions définies par le présent chapitre et est justifié par une cause réelle et sérieuse. :contentReference[oaicite:6]{index=6}

Article L1232-2 : L’employeur qui envisage de licencier un salarié le convoque, avant toute décision, à un entretien préalable. La convocation est faite par lettre recommandée ou remise en main propre et indique l’objet de la convocation. L’entretien ne peut avoir lieu moins de cinq jours ouvrables après la présentation de la lettre. :contentReference[oaicite:7]{index=7}

Article L1232-3 : Au cours de l’entretien préalable, l’employeur indique les motifs de la décision envisagée et recueille les explications du salarié. :contentReference[oaicite:8]{index=8}

Article L1232-4 : Le salarié peut se faire assister par une personne de son choix pendant l’entretien préalable, selon les règles du Code du travail. :contentReference[oaicite:9]{index=9}

Article L1232-5 : Un décret en Conseil d’Etat détermine les modalités d’application de la présente section. :contentReference[oaicite:10]{index=10}

Article L1242-1 : Un contrat de travail à durée déterminée, quel que soit son motif, ne peut avoir ni pour objet ni pour effet de pourvoir durablement un emploi lié à l’activité normale et permanente de l’entreprise. :contentReference[oaicite:11]{index=11}

Article L1243-1 : Sauf accord des parties, le contrat de travail à durée déterminée ne peut être rompu avant l’échéance du terme qu’en cas de faute grave, de force majeure ou d’inaptitude constatée par le médecin du travail. Lorsqu’il est conclu en application du 6° de l’article L1242-2, il peut aussi être rompu pour un motif réel et sérieux à partir de 18 mois après sa conclusion. :contentReference[oaicite:12]{index=12}

Article L1243-2 : Par dérogation, le CDD peut être rompu avant terme à l’initiative du salarié lorsqu’il justifie d’un CDI. Dans ce cas, il doit respecter un préavis d’un jour par semaine de contrat effectué (jusqu’à 2 semaines). :contentReference[oaicite:13]{index=13}

Article L1243-3 : La rupture anticipée du CDD à l’initiative du salarié en dehors des cas prévus ouvre droit à des dommages et intérêts. :contentReference[oaicite:14]{index=14}

Article L1243-4 : La rupture anticipée du CDD par l’employeur en dehors des cas prévus ouvre droit à des dommages et intérêts au salarié. :contentReference[oaicite:15]{index=15}

Article L1243-5 : Le contrat à durée déterminée cesse de plein droit à l’échéance du terme. :contentReference[oaicite:16]{index=16}

Article L1243-8 : Lorsque, à l’issue d’un CDD, il n’est pas poursuivi en CDI, le salarié a droit à une indemnité de fin de contrat destinée à compenser la précarité de sa situation. :contentReference[oaicite:17]{index=17}

Article L1243-9 : L’indemnité de fin de contrat peut être limitée par accord collectif sous conditions, notamment accès à la formation. :contentReference[oaicite:18]{index=18}

Article L1243-10 : L’indemnité de fin de contrat n’est pas due dans certains cas (ex : CDD saisonnier, refus CDI équivalent...). :contentReference[oaicite:19]{index=19}

Article L1243-11 : Si les relations de travail se poursuivent après l’échéance du CDD, il devient un CDI et l’ancienneté est conservée. :contentReference[oaicite:20]{index=20}

Article L2312-1 : Le chef d’entreprise organise les délégués du personnel pour présenter les réclamations individuelles et collectives. *(voir Légifrance pour texte complet)* :contentReference[oaicite:21]{index=21}

Article L2313-1 : Le comité social et économique (CSE) est institué dans les entreprises pour représenter les salariés. *(voir Légifrance pour texte complet)* :contentReference[oaicite:22]{index=22}

Article L4121-1 : L’employeur prend les mesures nécessaires pour assurer la sécurité et protéger la santé des travailleurs. *(voir Légifrance pour texte complet)* :contentReference[oaicite:23]{index=23}

Article L3121-1 : La durée du travail effectif des salariés est fixée par la loi. *(voir Légifrance pour texte complet)* :contentReference[oaicite:24]{index=24}
"""

code_civil_lois = """
Article 1 : Les lois sont exécutoires dans tout le territoire français en vertu de leur promulgation. Elles ne peuvent être rétroactives sauf disposition contraire. (Titre préliminaire – Code civil)

Article 2 : La loi ne dispose que pour l'avenir; elle n'a point d'effet rétroactif.

Article 3 : Les lois de police et de sûreté obligent tous ceux qui habitent le territoire. (Droit international privé et application des lois) :contentReference[oaicite:2]{index=2}

Article 5 : Il est défendu aux juges de prononcer par voie de disposition générale et réglementaire sur les causes qui leur sont soumises. (Juge comme interprète de la loi) :contentReference[oaicite:3]{index=3}

Article 7 : L'exercice des droits civils est indépendant de l'exercice des droits politiques. :contentReference[oaicite:4]{index=4}

Article 8 : Tout Français jouira des droits civils. :contentReference[oaicite:5]{index=5}

Article 9 : Chacun a droit au respect de sa vie privée. :contentReference[oaicite:6]{index=6}

Article 16 : La loi assure la primauté de la personne, interdit toute atteinte à la dignité de celle-ci et garantit le respect de l'être humain dès le commencement de la vie. :contentReference[oaicite:7]{index=7}

Article 16‑1 : Chacun a droit au respect de son corps. Le corps humain est inviolable; ses éléments ou produits ne peuvent faire l'objet d'un droit patrimonial. :contentReference[oaicite:8]{index=8}

Article 22 : La personne qui a acquis la nationalité française jouit de tous les droits et est tenue à toutes les obligations attachées à la qualité de Français. :contentReference[oaicite:9]{index=9}

Article 37 : Aucun juge ne peut refuser de juger sous prétexte du silence, de l’obscurité ou de l’insuffisance de la loi.

Article 1100 : Les règles de droit civil s’appliquent à toutes les personnes et à tous les biens, sauf dispositions légales contraires.

Article 1101 : Le contrat est un accord de volontés entre deux ou plusieurs personnes destiné à créer, modifier, transmettre ou éteindre des obligations.

Article 1121 : La stipulation pour autrui est un contrat par lequel une personne s’engage envers une autre à procurer un avantage à un tiers. (Droit des contrats) :contentReference[oaicite:10]{index=10}

Article 1134 : Les conventions légalement formées tiennent lieu de loi à ceux qui les ont faites. Elles doivent être exécutées de bonne foi.

Article 1147 : Le débiteur est condamné, s'il y a lieu, au paiement de dommages et intérêts lorsqu'il n'exécute pas ses obligations contractuelles.

Article 1382 : Tout fait quelconque de l'homme, qui cause à autrui un dommage, oblige celui par la faute duquel il est arrivé à le réparer. (Responsabilité civile délictuelle)

Article 1383 : Chacun est responsable du dommage qu'il a causé non seulement par son fait, mais encore par sa négligence ou son imprudence.

Article 1384 : On est responsable non seulement du dommage que l'on cause par son propre fait, mais encore de celui causé par le fait des personnes dont on doit répondre, ou des choses que l'on a sous sa garde.

Article 202 : Le mariage est contracté par consentement mutuel des futurs époux.

Article 212 : Les époux se doivent mutuellement fidélité, secours, assistance.

Article 221 : Le mariage ne peut être célébré avant la publication des bans.

Article 371‑1 : L'autorité parentale appartient aux parents jusqu'à la majorité ou l'émancipation de l’enfant. (Droit de la famille)

Article 515‑1 : Le PACS (pacte civil de solidarité) est un contrat conclu par deux personnes majeures pour organiser leur vie commune.

Article 534 : La propriété est le droit de jouir et disposer des choses de la manière la plus absolue, pourvu qu’on n’en fasse pas un usage prohibé par la loi.

Article 544 : La propriété est le droit de jouir et de disposer des biens de la manière la plus absolue, pourvu que l'on n’en fasse pas un usage prohibé par la loi.

Article 815 : Aucun copropriétaire ne peut être contraint à rester dans la indivision.

Article 2284 : Le testament ne peut être révoqué que par un autre testament.

Article 2276 : Le possesseur d’un bien est présumé propriétaire. (Bonne foi présumée)

"""

code_penal_lois = """
Article 111-1 : La loi pénale fixe les crimes, les délits et les contraventions ainsi que les peines qui leur sont applicables. (Principe de légalité des infractions et des peines) :contentReference[oaicite:2]{index=2}

Article 111-2 : Nul ne peut être puni d’une peine qui n’est pas prévue par la loi. (Principe de légalité) :contentReference[oaicite:3]{index=3}

Article 111-3 : Les dispositions de la loi pénale sont également applicables à l’infraction consommée ou tentée sur le territoire de la République. :contentReference[oaicite:4]{index=4}

Article 112-1 : La loi pénale ne peut rétroagir que si elle est plus douce pour l’auteur de l’infraction. :contentReference[oaicite:5]{index=5}

Article 121-1 : Nul n’est responsable pénalement que de son propre fait. (Responsabilité personnelle) :contentReference[oaicite:6]{index=6}

Article 121-2 : Les personnes morales, à l’exclusion de l’État, sont responsables pénalement, selon les distinctions des articles 121-4 à 121-7, des infractions commises pour leur compte par leurs organes ou représentants. :contentReference[oaicite:7]{index=7}

Article 122-1 : N’est pas pénalement responsable la personne qui prouve avoir accompli l’acte sous l’empire d’une force ou contrainte qui ne lui laisse aucun choix raisonnable d’agir autrement. :contentReference[oaicite:8]{index=8}

Article 122-2 : N’est pas pénalement responsable celui qui accomplit l’acte prescrit ou autorisé par des dispositions législatives ou réglementaires. :contentReference[oaicite:9]{index=9}

Article 131-1 : Les peines applicables sont celles prévues par la loi en vigueur lors de la commission de l’infraction. :contentReference[oaicite:10]{index=10}

Article 131-2 : Les peines peuvent être : l’emprisonnement, l’amende, les peines complémentaires, et les peines privatives ou restrictives de droits. :contentReference[oaicite:11]{index=11}

Article 132-1 : Toute peine prononcée par la juridiction doit être individualisée; dans les limites fixées par la loi, la juridiction détermine la nature, le quantum et le régime des peines. :contentReference[oaicite:12]{index=12}

Article 211-1 : Le meurtre est puni de trente ans de réclusion criminelle lorsqu’il n’est pas qualifié par la présente loi. :contentReference[oaicite:13]{index=13}

Article 221-1 : Les violences volontaires sont punies de trois ans d’emprisonnement et de 45 000 € d’amende lorsqu’elles n’ont entraîné aucune incapacité totale de travail. :contentReference[oaicite:14]{index=14}

Article 221-4 : La violence ayant entraîné une incapacité totale de travail pendant plus de huit jours est punie de cinq ans d’emprisonnement et de 75 000 € d’amende. :contentReference[oaicite:15]{index=15}

Article 222-1 : Le viol est puni de quinze ans de réclusion criminelle. :contentReference[oaicite:16]{index=16}

Article 222-22 : Le viol est défini comme tout acte de pénétration sexuelle, de quelque nature qu’il soit, commis par violence, contrainte, menace ou surprise. :contentReference[oaicite:17]{index=17}

Article 311-1 : Le vol est puni de trois ans d’emprisonnement et de 45 000 € d’amende. :contentReference[oaicite:18]{index=18}

Article 313-1 : L’escroquerie est punie de cinq ans d’emprisonnement et de 375 000 € d’amende. :contentReference[oaicite:19]{index=19}

Article 314-1 : L’abus de confiance est puni de cinq ans d’emprisonnement et de 375 000 € d’amende. :contentReference[oaicite:20]{index=20}

Article 322-1 : La destruction, dégradation ou détérioration d’un bien appartenant à autrui est punie de deux ans d’emprisonnement et de 30 000 € d’amende. :contentReference[oaicite:21]{index=21}

Article 432-1 : Le fait d’entraver l’action de la justice ou de la police judiciaire est puni de cinq ans d’emprisonnement et de 75 000 € d’amende. :contentReference[oaicite:22]{index=22}
"""

docs = [{"doc_info":"code penal","doc_text":code_penal_lois},{"doc_info":"code civil", "doc_text":code_civil_lois},{"doc_info":"code du travail", "doc_text":code_travail_lois}]

context = initialize_context("You're a really talented lawyer assistant", "Find for me pertinent law text about SA in US") 
output = generate_response_openai(context, "deepseek-chat","https://api.deepseek.com/v1/chat/completions")

print(output)


knowledgebase = build_knowledgebase(docs)
print(f"\n{'='*60}")
print(f"Knowledge base: {len(knowledgebase.get('embeddings', []))} embeddings, {len(knowledgebase.get('docs', []))} documents")
print(f"{'='*60}")

results = retrieve_relevant_doc("Mon amis m'a pîégé pour volé mon billet de loto (ou j'ai gagné 1000000€)", knowledgebase)

if results:
	print(f"\n{'='*60}")
	print(f"Documents pertinents trouvés: {len(results)}")
	print(f"{'='*60}\n")
	for i, result in enumerate(results, 1):
		print(f"[{i}] {result['doc']['doc_info'].upper()}")
		print(f"    Pertinence: {result['score']:.4f}")
		print()
else:
	print("\nAucun document trouvé.")

