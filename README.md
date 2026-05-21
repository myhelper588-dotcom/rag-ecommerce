# RAG eCommerce — Assistant PDF Intelligent

Système de questions-réponses intelligent basé sur vos documents,
utilisant LangChain, ChromaDB et l'API Claude d'Anthropic.

## Architecture

- **LangChain** — Orchestration du pipeline RAG
- **ChromaDB** — Base vectorielle locale
- **Claude API** — Génération des réponses
- **Docker** — Environnement containerisé portable

## Prérequis

- Docker Desktop installé et démarré
- Clé API Anthropic (console.anthropic.com)

## Installation

### 1. Cloner le projet
git clone https://github.com/myhelper588-dotcom/rag-ecommerce.git
cd rag-ecommerce

### 2. Configurer la clé API
Créer un fichier .env à la racine :
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

### 3. Ajouter un PDF
Copier votre document PDF dans le dossier data/ :
data/document.pdf

### 4. Lancer le projet
docker-compose build
docker-compose run rag-app

## Utilisation
Une fois lancé, posez vos questions directement dans le terminal.
Tapez quit pour quitter.

## Cas d'usage eCommerce
- Analyse de cahiers des charges techniques
- Questions sur des appels d'offres
- Exploration de documentations AWS
- Analyse de spécifications produit

## Roadmap
- [x] RAG mono-PDF fonctionnel
- [ ] Support multi-PDF avec filtrage metadata
- [ ] Interface web FastAPI
- [ ] Déploiement AWS EC2
- [ ] Monitoring LangSmith

## Stack technique
| Composant | Technologie |
|-----------|-------------|
| LLM | Claude claude-opus-4-5 |
| Orchestration | LangChain |
| Vector Store | ChromaDB |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Container | Docker |
| Cloud | AWS EC2 (Projet 3) |