# Medical RAG Chatbot

Application full-stack **RAG** (Retrieval-Augmented Generation) orientée information médicale générale : récupération dans **ChromaDB**, réponses via **LLM** avec citations. Le backend est structuré en couches (domaine, ports, infra), avec observabilité (latence, métriques) et résilience (timeouts, circuit breaker).

---

## Stack

| Couche | Technologie |
|--------|-------------|
| API | Python 3.11, FastAPI, Uvicorn |
| Frontend | React 18, TypeScript, MUI |
| Vecteurs & embeddings | ChromaDB, Sentence-Transformers (`all-MiniLM-L6-v2` par défaut) |
| LLM | **Ollama** (local) ou **Groq** (cloud), sélection via `LLM_PROVIDER` |
| Chaîne RAG | LangChain 0.3+ (LCEL : retriever → prompt → chat → parser) |
| Tests | pytest, httpx (ASGI) |

---

## Prérequis

- **Python 3.11+** et **Node.js 18+**
- Pour le mode local LLM : [Ollama](https://ollama.com/) + au moins un modèle (ex. `ollama pull llama3.2:1b`)
- Pour le mode cloud : clé API [Groq](https://console.groq.com/) et `LLM_PROVIDER=groq`

---

## Installation

À la racine du dépôt (venv recommandé) :

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
pip install -r requirements-dev.txt   # pour lancer les tests
cd frontend && npm install && cd ..
```

Copier `.env.example` vers `.env` et ajuster `LLM_PROVIDER`, `GROQ_API_KEY` si besoin.

---

## Lancer en développement

Le backend doit tourner sur le **port 8000**, le frontend sur **3000** (l’UI appelle l’API en `http://localhost:8000`).

**Windows (deux fenêtres)** — depuis la racine :

```powershell
.\scripts\start-dev.ps1
```

**Manuellement**

1. `cd backend` → `python main.py` (Swagger : http://127.0.0.1:8000/docs)  
2. `cd frontend` → `npm start` → http://localhost:3000  

Ne pas définir `TESTING=1` : le bootstrap RAG serait ignoré.

---

## Tests

Depuis la racine :

```bash
pytest tests/
```

---

## Docker

```bash
docker build -t medical-rag .
docker run -p 8000:8000 --env-file .env medical-rag
```

Image : `python:3.11-slim`, port **8000**, voir `Dockerfile` et `.dockerignore`.

---

## CI/CD (AWS ECS Fargate)

Sur push vers **`main`**, le workflow `.github/workflows/deploy.yml` construit l’image, la pousse vers **ECR** et déclenche un redéploiement du service **ECS**.

Secrets GitHub typiques : `AWS_REGION`, `ECR_REGISTRY`, `ECR_REPOSITORY`, `ECS_CLUSTER`, `ECS_SERVICE`, ainsi que des identifiants AWS (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) ou OIDC selon ta configuration IAM.

---

## Structure du dépôt

```
MedicalRAGChatbot/
├── backend/              # FastAPI — domain/, infra/, api/, resilience/, exceptions/
├── frontend/             # React (CRA + TypeScript)
├── tests/                # Pytest
├── scripts/              # start-dev.ps1, start-dev.sh
├── docs/                 # notes optionnelles (ex. warm-up embeddings)
├── .github/workflows/    # déploiement ECS
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── pyproject.toml
```

---

## Configuration

Variables principales : voir **`.env.example`** (`LLM_PROVIDER`, `GROQ_API_KEY`, `GROQ_MODEL`, chemins Chroma/cache embeddings, etc.). Détail des clés dans `backend/domain/config.py`.

---

## Premier lancement (warm-up)

Au **premier** démarrage, le modèle d’embeddings Hugging Face est téléchargé puis chargé (souvent plusieurs minutes selon réseau et CPU). Les lancements suivants sont plus rapides si le cache (`EMBEDDING_CACHE_FOLDER`) est conservé. Sur ECS/Fargate, prévoir volume persistant pour `chroma_db` et le cache modèles si tu ne veux pas tout retélécharger à chaque tâche.

---

## Avertissement

Outil **pédagogique / démonstration** — ne remplace pas un avis médical professionnel. Les réponses peuvent être incomplètes ou erronées ; en cas de symptômes graves, contacter les services d’urgence.

---

## Licence

MIT (voir fichier `LICENSE` s’il est présent dans le dépôt).
