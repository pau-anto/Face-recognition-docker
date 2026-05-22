# =========================================================
# Dockerfile.app — Application ML Flask
# Harry Potter Face Recognition
# Stack : Python 3.11 · Flask · FaceNet-PyTorch · SQLAlchemy
# Port  : 5000
# =========================================================

# ── Stage 1 : builder ─────────────────────────────────────
# Sépare l'installation des dépendances lourdes (PyTorch)
# de l'image finale pour un cache Docker plus efficace.
FROM python:3.11-slim AS builder

WORKDIR /build

# Dépendances système nécessaires à la compilation
# (Pillow → libjpeg/zlib ; torch → libgomp ; pymysql → libssl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement le fichier de dépendances d'abord
# → Docker met en cache cette couche tant que requirements.txt ne change pas
COPY database/requirements.txt .

# Installer toutes les dépendances Python dans un dossier isolé
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2 : image finale ────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="pau-anto"
LABEL project="hp-face-recognition"
LABEL description="Flask ML app — Face recognition des acteurs Harry Potter"

# ── Dépendances runtime uniquement (pas les outils de compilation) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libjpeg62-turbo \
    zlib1g \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Copier les packages Python installés depuis le builder ─
COPY --from=builder /install /usr/local

# ── Répertoire de travail ─────────────────────────────────
WORKDIR /app



# ── Copier le code source ─────────────────────────────────
# L'ORM de la BD (utilisé par l'app pour écrire les prédictions)
COPY database/database.py     ./database/database.py
COPY database/schema.sql      ./database/schema.sql

# Le code applicatif Flask + reconnaissance faciale
# (main.py · recognition.py · utils.py · config.py)
COPY app/                     ./app/

# ── Variables d'environnement ─────────────────────────────
# Valeurs par défaut — à surcharger dans docker-compose ou --env-file
ENV DB_HOST=db
ENV DB_PORT=3306
ENV DB_USER=wpuser
ENV DB_PASSWORD=wppass
ENV DB_NAME=hp_recognition

# Configuration Flask
ENV FLASK_APP=app/main.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Python : pas de .pyc, logs non bufferisés (visibles dans docker logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── Dossier pour les données images du dataset Kaggle ─────
RUN mkdir -p /data/images

# ── Port exposé ───────────────────────────────────────────
EXPOSE 5000

# ── Healthcheck ───────────────────────────────────────────
# Vérifie que l'API Flask répond (endpoint /health à créer dans main.py)
HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# ── Script de démarrage ───────────────────────────────────
# Attend que MySQL soit disponible avant de lancer Flask.
# Utilise une boucle simple avec curl sur le port 3306.
COPY docker/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# ── Point d'entrée ────────────────────────────────────────
ENTRYPOINT ["/wait-for-db.sh"]
CMD ["python", "app/main.py"]
