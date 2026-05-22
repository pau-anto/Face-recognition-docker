# 🧙‍♂️ Harry Potter Face Recognition with Docker

**Projet de fin de trimestre** - Reconnaissance faciale des acteurs Harry Potter containerisée avec Docker.

**Groupe:** 3 personnes | **Deadline:** 5 juin 2026

---

## 📋 Vue d'ensemble

Ce projet combine **Machine Learning** (reconnaissance faciale via FaceNet), **gestion de base de données** (MySQL), et **DevOps** (Docker) pour :
- Extraire des **embeddings faciaux** (vecteurs 128D) des acteurs Harry Potter
- **Prédire** l'identité des personnages dans les images
- **Persister** les résultats dans une BD MySQL
- **Visualiser** les résultats via une interface web

### Dataset
[Harry Potter Cast Face Recognition - Kaggle](https://www.kaggle.com/datasets/alexday11/harry-potter-cast-face-recognition)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│      Docker Network: app_network            │
│                                             │
│  ┌─────────────┐  ┌──────────┐  ┌────────┐  │
│  │  App ML     │  │  MySQL   │  │ Nginx  │  │
│  │  (Flask)    │─→│   (DB)   │←─│ (Web)  │  │
│  │  Port 5000  │  │Port 3306 │  │Port 80 │  │
│  └─────────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────────┘
```

**3 containers :**
- **App ML** (Port 5000) - Logique de reconnaissance faciale
- **MySQL** (Port 3306) - Persistance des données
- **Nginx** (Port 80) - Interface web et visualisation

---

## 📁 Structure du projet

```
hp-face-recognition-docker/
├── README.md                    ← Ce fichier
├── .gitignore
│
├── app/                         # Application ML (Flask/FastAPI)
│   ├── main.py
│   ├── recognition.py
│   ├── utils.py
│   └── config.py
│
├── database/                    # Gestion base de données
│   ├── schema.sql
│   ├── database.py              # ORM
│   └── migrations/
│
├── docker/                      # Configuration Docker
│   ├── Dockerfile.app
│   ├── Dockerfile.db
│   ├── Dockerfile.web
│   └── docker-compose.yml
│
├── notebooks/                   # Jupyter notebooks
│   └── Defi20_reconnaissance_harry_potter_faces.ipynb
│
├── frontend/                    # React / Frontend
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── api-client.js
│
├── tests/                       # Tests unitaires
│   └── test_database.py
│
└── docs/                        # Documentation
    ├── ARCHITECTURE.md
    ├── SETUP.md
    └── API.md
```

---

## 🚀 Quick Start

### Prérequis
- Python 3.11+
- Docker & Docker Compose
- MySQL (ou MariaDB)
- Git

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/YOUR_USERNAME/hp-face-recognition-docker.git
cd hp-face-recognition-docker

# 2. Créer les branches par domaine
git checkout -b database/schema          # Pour la BD
git checkout -b docker/architecture      # Pour Docker
git checkout -b frontend/web-interface   # Pour le frontend
```

### Lancer localement

```bash
# 1. Setup MySQL
mysql -u root -p < database/schema.sql

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'app
python app/main.py
```

### Avec Docker

```bash
# 1. Build les images
docker-compose build

# 2. Lancer les containers
docker-compose up -d

# 3. Vérifier le statut
docker-compose ps
```

---

## 📊 Schéma de la BD

**5 tables principales :**

```sql
characters         -- Acteurs/Personnages Harry Potter (16)
images             -- Photos du dataset
embeddings         -- Vecteurs faciales (128D)
predictions        -- Historique des prédictions
execution_logs     -- Stats d'exécution
```

---

*Projet académique — ESGI — Conteneurisation logicielle — Juin 2026*
