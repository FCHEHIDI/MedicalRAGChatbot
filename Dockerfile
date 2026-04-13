# Medical RAG Chatbot — production image (FastAPI sur le port 8000)
# Multi-stage : réduit la taille finale tout en permettant les wheels compilés (Chroma, etc.)

FROM python:3.11-slim AS builder
WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# libgomp1 : utile pour certaines libs numériques (torch / sentence-transformers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend

COPY backend/ ./backend/

EXPOSE 8000

# Fargate : définir LLM_PROVIDER, GROQ_API_KEY, etc. dans la task definition ou SSM
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
