================================================================================
  FACE RECOGNITION DOCKER — Harry Potter Character Recognizer
  Branche : structure-docker
  Projet  : 4IABD
================================================================================

DESCRIPTION DU PROJET
----------------------
Application web de reconnaissance faciale de personnages de la saga Harry Potter,
déployée dans une architecture microservices Docker.

L'utilisateur upload une image via une interface web (Streamlit), l'image est
envoyée à une API de reconnaissance faciale, et le résultat (personnage identifié
+ score de confiance) est affiché à l'écran. Les prédictions sont enregistrées
dans une base de données MySQL.

ARCHITECTURE
------------
Le projet est structuré en 3 services Docker :

  1. frontend/    — Interface utilisateur Streamlit (port 8501)
  2. api/         — Service de reconnaissance faciale (port 8000) [non inclu dans ce zip]
  3. database/    — Base de données MySQL avec table predictions

STRUCTURE DES FICHIERS
----------------------
Face-recognition-docker/
├── frontend/
│   ├── app.py              # Application Streamlit principale
│   ├── appv2.py            # Version expérimentale de l'app
│   ├── Dockerfile          # Image Docker du frontend (python:3.11-slim)
│   ├── requirements.txt    # Dépendances : streamlit, requests, Pillow
│   └── tests/
│       └── test_app.py     # Tests unitaires du frontend
├── database/
│   ├── init.sql            # Script d'initialisation de la BDD MySQL
│   └── tests/
│       └── test_schema.sql # Tests de validation du schéma SQL
└── .gitignore              # Fichiers exclus du dépôt Git

TECHNOLOGIES UTILISÉES
-----------------------
  - Python 3.11
  - Streamlit 1.32.0       (interface utilisateur)
  - Requests 2.31.0        (appels HTTP vers l'API)
  - Pillow 10.2.0           (traitement d'images)
  - MySQL                   (persistance des prédictions)
  - Docker / Docker Compose (containerisation)

SCHÉMA DE BASE DE DONNÉES
--------------------------
Base de données : hpdb
Table : predictions
  - id             INT AUTO_INCREMENT PRIMARY KEY
  - character_name VARCHAR(100) NOT NULL
  - confidence     FLOAT NOT NULL
  - created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP

LANCEMENT DU PROJET
--------------------
  # Construire et lancer tous les services
  docker-compose up --build

  # Accéder à l'interface web
  http://localhost:8501

  # L'API doit être accessible en interne sur
  http://api:8000/analyze/

VARIABLES D'ENVIRONNEMENT
--------------------------
  API_URL   URL interne de l'API (défaut : http://api:8000)

FONCTIONNEMENT DE L'APPLICATION
---------------------------------
  1. L'utilisateur upload une image JPG/PNG via l'interface
  2. L'image est envoyée en POST à l'endpoint /analyze/ de l'API
  3. L'API retourne le nom du personnage et un score de confiance (0 à 1)
  4. L'interface affiche le résultat avec badge de maison (Gryffondor,
     Serpentard, Serdaigle, Poufsouffle) et indicateur de statut de l'API
  5. La prédiction est enregistrée dans la base de données MySQL

PRÉREQUIS
----------
  - Docker >= 20.x
  - Docker Compose >= 2.x

AUTEUR
-------
  Projet académique — 4IABD
  Dépôt : https://github.com/pau-anto/Face-recognition-docker
  Branche : structure-docker

================================================================================
