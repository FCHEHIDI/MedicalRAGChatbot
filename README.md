# Medical RAG Chatbot

Assistant médical (RAG) : **React** + **FastAPI** + **ChromaDB** + **Sentence-Transformers** + **LLM** (**Ollama** en local ou **Groq** en cloud, voir `LLM_PROVIDER`).

## Prérequis

- Python **3.11+**
- Node.js **18+**
- [Ollama](https://ollama.com/) si `LLM_PROVIDER=ollama` (ex. `ollama pull llama3.2:1b`)
- Compte [Groq](https://console.groq.com/) si `LLM_PROVIDER=groq`

## Installation

À la racine du dépôt :

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # optionnel : tests
cd frontend && npm install && cd ..
```

## Lancer en local

**Option A — deux terminaux**

1. Backend (depuis `backend/`, venv activé) : `python main.py` → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
2. Frontend : `cd frontend && npm start` → [http://localhost:3000](http://localhost:3000)

**Option B — Windows**

```powershell
.\scripts\start-dev.ps1
```

Ne pas définir `TESTING=1` pour un run normal (sinon le RAG ne s’initialise pas).

## Tests

```bash
pytest tests/
```

## Structure utile

```
MedicalRAGChatbot/
├── backend/           # API FastAPI (domain/, infra/, api/, resilience/)
├── frontend/          # React (CRA + TypeScript)
├── tests/             # Pytest
├── scripts/           # start-dev.ps1 / start-dev.sh
├── .github/workflows/ # CI/CD ECS
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── pyproject.toml
```

## Variables d’environnement

Voir `.env.example` (`LLM_PROVIDER`, `GROQ_API_KEY`, etc.).

## Déploiement (Docker & AWS ECS)

- Image : `Dockerfile` à la racine (Python 3.11-slim, port **8000**).
- Build local : `docker build -t medical-rag .` puis `docker run -p 8000:8000 --env-file .env medical-rag`
- CI/CD : push sur **`main`** → workflow `.github/workflows/deploy.yml` (build → ECR → `ecs update-service`).  
  Secrets GitHub : `AWS_REGION`, `ECR_REGISTRY`, `ECR_REPOSITORY`, `ECS_CLUSTER`, `ECS_SERVICE`, et **identifiants IAM** `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` pour l’étape AWS CLI (ou remplacer par OIDC selon ton compte).

## Notes

- Premier démarrage : téléchargement du modèle d’embeddings (Hugging Face) — peut prendre plusieurs minutes. Voir `docs/WARMUP_REPORT.md`.
- Variables utiles : `EMBEDDING_MODEL`, `EMBEDDING_CACHE_FOLDER`, `CHROMADB_PATH` (voir `backend/domain/config.py`).
