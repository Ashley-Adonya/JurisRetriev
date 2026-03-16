# JurisRetriev

JurisRetriev est un système de RAG (Retrieval-Augmented Generation) spécialisé dans l'analyse et l'assistance juridique. Le système intègre des modèles de langage de grande taille (LLM) et des bases de données vectorielles pour fournir des réponses argumentées. Il intègre un mécanisme de stockage en mémoire pour les contextes temporaires et MongoDB pour l'analytics et la gestion des utilisateurs.

## Origine du système

L'application a été conçue pour surmonter les limitations des processus juridiques traditionnels basés uniquement sur la recherche par mot-clé, souvent lents et moins performants face à des masses documentaires non structurées. JurisRetriev permet une recherche sémantique intelligente couplée à un moteur génératif capable d'interpréter, de reformuler des requêtes complexes en termes juridiques, et de générer une défense ou une contre-argumentation solide.

## Technologies Utilisées

*   **Backend** : Python 3.12, Flask 3.0+
*   **Base de données** : MongoDB (via `PyMongo`)
*   **Intelligence Artificielle** : API DeepSeek (Génération/Formatage structuré en Chat), Jina Embeddings (`jina-embeddings-v5-text-small`)
*   **Mathématiques & Vecteurs** : NumPy (Calcul local de similarité Cosinus) - Les données du chat sont indexées dynamiquement in-memory.
*   **Frontend** : HTML5, Vanilla JavaScript, Tailwind CSS, Jinja Templating
*   **Sécurité** : JWT (JSON Web Tokens) RSA/Stateless sans stockage de session en base. Email via SMTP.

## Architecture du Système & Principes de conception

Le projet est articulé autour d'une architecture orientée API et d'un frontend web structuré via des vues directes :

1.  **Paradigme Impératif / Fonctionnel (No-OOP)** :  
    Le backend a été écrit de façon strictement fonctionnelle. L'utilisation des classes est proscrite pour la gestion de la BDD et le traitement des requêtes, afin de conserver un flux de données linéaire et transparent (scripts sous forme de dictionnaires bruts pour attaquer MongoDB).

2.  **Séparation de l'Interface (Jinja & SPA Logic)** :  
    L'UI est découpée via les templates Jinja de Flask (`base.html`, `landing.html`, `chat.html`, `admin.html`, `contact.html`). Le contrôle client (JavaScript) mappe les permissions d'utilisateur selon des flags sécurisés lors de l'authentification (`is_admin`).

3.  **Système RAG Dynamique à Contexte Restreint** :  
    Afin de protéger la confidentialité des contextes juridiques, le processus n'enregistre **pas** vos documents indéfiniment. Il stocke les documents fraîchement uploadés dans un cache mémoire tournant et efface l'index temporaire lorsqu'il gagne en volume (au-delà de 4 documents). Le système ne base son interprétation que sur la portée fraîchement injectée.

4.  **Limitation & Quotas par Utilisateur** :  
    Pour minimiser les coûts des API LLM, JurisRetriev intègre une limite stricte de requêtes : via les collections MongoDB `usage_counters`, l'app bloque à **5 requêtes maximum par jour/utilisateur**.

## Prérequis

1. Python 3.12 (Recommandé) ou version ultérieure.
2. Serveur MongoDB distant ou local s'exécutant sur `localhost:27017`.
3. Clés API : 
    *   **OpenAI / DeepSeek** : Pour la génération LLM
    *   **Jina API** : Pour les embeddings vectoriels

## Configuration de base

1. Création d'un environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate

   # Sous Windows : .venv\Scripts\activate
   ```

2. Installation des dépendances du projet :
   ```bash
   pip install -r requirements.txt
   ```
   *(Les dépendances incluent Flask, pymongo, requests, PyJWT, numpy, etc.)*

3. Fichier d'environnement (`.env`) :
   Créez un fichier `.env` à la racine pour votre configuration locale. Vous devez obligatoirement remplir les paramètres API et JWT. Voici le template par défaut :
   ```env
    OPENAI_API_KEY=sk-...
    JINA_API_KEY=jina_...
    JINA_MODEL=jina-embeddings-v5-text-small
    JWT_SECRET=super_secret_aleatoire

    # Compte Administrateur Root (Auto-généré dans MongoDB au démarrage)
    ADMIN_EMAIL=admin@jurisretriev.com
    ADMIN_PASSWORD=SuperAdmin123!

    # Configuration MongoDB (Par défaut: Local)
    MONGODB_URI=mongodb://127.0.0.1:27017
    MONGODB_DB=jurisretriev

    # Configuration Email / SMTP (Optionnel : Sans quoi, des faux emails sont logs dans le terminal)
    SMTP_SERVER=
    SMTP_PORT=587
    SMTP_USER=
    SMTP_PASSWORD=
    MAIL_DEFAULT_SENDER=noreply@jurisretriev.com
   ```

## Lancement & Utilisation

Pour lancer le serveur de l'application :

```bash
python server.py
```

*Remarque : Au démarrage, `server.py` lit le `.env` pour importer dynamiquement les index MongoDB et le compte administrateur racine.*

### Structure de Navigation (port par défaut : `5000`)

- **`/` (Landing Page)** : Accueil principal
- **`/chat` (L'Assistant)** : L'espace d'upload documentaire (RAG) et de conversation. Limité par les quotas de la BDD.
- **`/admin` (Dashboard)** : Panneau de supervision des statistiques globales (Requêtes totales et inscrits). Affiché via flag `isAdmin` du stockage Web local.
- **`/contact`** : Page de support en cas de pannes et de contact en cas de limites atteintes (Hors ligne et public).

## Déploiement sur Vercel

Le projet a été formaté pour être facilement déployable de manière "Serverless" et gratuite via **Vercel**.

1. Connectez votre dépôt GitHub à **Vercel**.
2. Créez un nouveau projet et sélectionnez le dépôt.
3. Lors de la configuration du projet sur Vercel :
    - Laissez le `Framework Preset` sur **Other**.
    - Dans la section **Environment Variables**, ajoutez TOUTES les variables présentes dans votre `.env` local (`MONGODB_URI`, `JWT_SECRET`, `JINA_API_KEY`, etc.).
4. Déployez ! 

Vercel lira par défaut le fichier `vercel.json` qui se chargera d'invoquer `server.py` et d'initialiser correctement votre cluster d'administration et vos index MongoDB à la volée.
