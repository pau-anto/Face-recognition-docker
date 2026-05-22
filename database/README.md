# 💾 Database - Harry Potter Face Recognition

Guide complet pour déployer et utiliser la base de données MySQL avec Python.

---

## 📋 Contenu du dossier `database/`

```
database/
├── schema.sql           # Structure de la BD (5 tables)
├── database.py          # ORM Python (interface BD)
├── requirements.txt     # Dépendances Python
├── test_database.py     # Tests automatisés
└── README.md            # Ce fichier
```

---

## 🚀 Déploiement rapide (Docker)

### Option 1: Avec Docker (Recommandé)

```bash
# À la racine du projet
docker-compose -f docker/docker-compose-test.yml up -d

# Attendre ~30 secondes que MySQL démarre

# Vérifier que la BD est prête
docker exec hp-db-test mysql -u root -proot_password hp_recognition -e "SHOW TABLES;"
```

**Résultat attendu:**
```
+------------------------+
| Tables_in_hp_recognition |
+------------------------+
| characters             |
| embeddings             |
| execution_logs         |
| images                 |
| predictions            |
+------------------------+
```

### Option 2: MySQL local

```bash
# Créer la BD
mysql -u root -p < database/schema.sql

# Vérifier
mysql -u root -p hp_recognition -e "SHOW TABLES;"
```

---

## 📦 Installation des dépendances Python

```bash
pip install -r database/requirements.txt
```

**Dépendances principales:**
- `sqlalchemy==2.0.23` - ORM Python
- `pymysql==1.1.0` - Connecteur MySQL
- `numpy==1.24.3` - Pour les vecteurs (embeddings)
- `flask==3.0.0` - API web (optionnel)

---

## 💻 Utiliser la BD en Python

### Exemple basique

```python
from database import Database

# 1. Se connecter
db = Database(
    user="wpuser",
    password="wppass",
    host="localhost",
    port=3306,
    database="hp_recognition"
)

# 2. Créer les tables (si première utilisation)
db.create_tables()

# 3. Ajouter une image
image = db.add_image(
    character_name="Harry Potter",
    file_path="/data/images/harry_001.jpg",
    file_name="harry_001.jpg",
    image_size=102400,
    dataset_type="train"
)

# 4. Ajouter un embedding (vecteur facial)
import numpy as np
embedding_vector = np.random.rand(128)  # 128D vector de FaceNet
db.add_embedding(
    image_id=image.id,
    character_id=4,  # ID de Harry Potter
    embedding_vector=embedding_vector,
    processing_time_ms=45
)

# 5. Ajouter une prédiction
db.add_prediction(
    image_id=image.id,
    predicted_character_id=4,
    predicted_character_name="Harry Potter",
    true_character_id=4,
    confidence_score=0.95,
    distance=0.25,
    inference_time_ms=120,
    run_id="run_2026_05_22"
)

# 6. Récupérer les stats
stats = db.get_global_stats()
print(f"Accuracy: {stats['accuracy_percent']}%")

# 7. Exporter en JSON
db.export_predictions_to_json(
    run_id="run_2026_05_22",
    output_file="predictions.json"
)
```

---

## 📚 Classe Database - Méthodes disponibles

### Images

```python
# Ajouter une image
image = db.add_image(
    character_name="Harry Potter",
    file_path="/data/harry_001.jpg",
    file_name="harry_001.jpg",
    image_size=102400,
    dataset_type="train"  # 'train', 'test', ou 'validation'
)

# Récupérer les images d'un personnage
images = db.get_images_by_character("Harry Potter")
for img in images:
    print(f"- {img.file_name}: {img.image_size} bytes")
```

### Embeddings (Vecteurs faciaux)

```python
import numpy as np

# Ajouter un embedding
embedding_vector = np.random.rand(128).astype(np.float32)
emb = db.add_embedding(
    image_id=1,
    character_id=4,
    embedding_vector=embedding_vector,
    processing_time_ms=45
)

# Récupérer les embeddings
embeddings = db.get_all_embeddings()
for emb in embeddings:
    vector = emb.get_embedding()  # Récupère le vecteur numpy
    print(f"Vector shape: {vector.shape}")
```

### Prédictions

```python
# Ajouter une prédiction
pred = db.add_prediction(
    image_id=1,
    predicted_character_id=4,      # Qu'on a prédit
    predicted_character_name="Harry Potter",
    true_character_id=4,            # Le vrai
    confidence_score=0.95,          # 0.0 à 1.0
    distance=0.25,                  # Distance euclidienne
    inference_time_ms=120,
    run_id="run_2026_05_22"
)

# Récupérer les prédictions récentes
predictions = db.get_recent_predictions(limit=100)
for p in predictions:
    print(f"Prédiction {p['id']}: confiance {p['confidence']}")
```

### Statistiques

```python
# Stats globales
stats = db.get_global_stats()
print(f"""
Total prédictions: {stats['total_predictions']}
Correctes: {stats['correct_predictions']}
Accuracy: {stats['accuracy_percent']}%
Confiance moyenne: {stats['avg_confidence']:.4f}
""")

# Stats par personnage
accuracy_by_char = db.get_character_accuracy()
for char_name, stats in accuracy_by_char.items():
    print(f"{char_name}: {stats['accuracy']}% ({stats['correct']}/{stats['total']})")

# Récupérer tous les personnages
characters = db.get_all_characters()
for char in characters:
    print(f"- {char['name']} ({char['actor']})")
```

### Logs d'exécution

```python
# Sauvegarder un log après une exécution complète
db.save_execution_log(
    run_id="run_2026_05_22",
    total_images=1000,
    correct_predictions=950,
    total_processing_time_s=123.45,
    avg_inference_time_ms=120.5,
    notes="Test sur dataset complet"
)
```

### Export/Import

```python
# Exporter les prédictions en JSON
json_str = db.export_predictions_to_json(
    run_id="run_2026_05_22",
    output_file="predictions.json"
)

# Vérifier le contenu
import json
data = json.loads(json_str)
print(f"{len(data)} prédictions exportées")
```

---

## 🧪 Tester la BD

```bash
# Lancer les tests
python database/test_database.py
```

**Résultat attendu:**
```
======================================================================
🧙‍♂️  TESTS BASE DE DONNÉES - Harry Potter Face Recognition
======================================================================

🔍 Test 1: Connexion à MySQL...
✅ Connexion réussie!

🔍 Test 2: Création des tables...
✅ Tables créées/vérifiées!

🔍 Test 3: Récupération des personnages...
✅ 16 personnages trouvés:
   - Severus Snape (Alan Rickman)
   - Dean Thomas (Alfred Enoch)
   - Ginny Weasley (Bonnie Wright)
   ... et 13 autres

... (autres tests)

======================================================================
✅ TOUS LES TESTS SONT TERMINÉS!
======================================================================

🎉 Votre BD est prête à l'emploi!
```

---

## 🗂️ Schéma de la BD

### characters (16 acteurs)
```sql
id (PK) | name              | actor_name       | description
1       | Severus Snape     | Alan Rickman     | NULL
2       | Harry Potter      | Daniel Radcliffe | NULL
...     | ...               | ...              | ...
```

### images (Photos du dataset)
```sql
id (PK) | character_id (FK) | file_path         | dataset_type | image_size
1       | 2                 | /data/harry_1.jpg | train        | 102400
2       | 2                 | /data/harry_2.jpg | test         | 98304
...
```

### embeddings (Vecteurs 128D)
```sql
id (PK) | image_id (FK) | character_id (FK) | embedding_vector (binaire) | embedding_dim
1       | 1             | 2                 | [binary data of 128 floats] | 128
2       | 2             | 2                 | [binary data of 128 floats] | 128
...
```

### predictions (Historique)
```sql
id (PK) | image_id (FK) | predicted_char_id | true_char_id | confidence | is_correct | run_id
1       | 1             | 2                 | 2            | 0.95       | TRUE       | run_001
2       | 2             | 3                 | 2            | 0.42       | FALSE      | run_001
...
```

### execution_logs (Stats)
```sql
run_id     | total_images | correct_predictions | accuracy | total_time_s | avg_inference_ms
run_001    | 1000         | 950                 | 95.0     | 120.5        | 120.5
run_002    | 500          | 475                 | 95.0     | 60.2         | 120.4
...
```

---

## 🔌 Connexion à la BD

### Configuration

**Variables d'environnement (.env):**
```
DB_USER=wpuser
DB_PASSWORD=wppass
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hp_recognition
```

**Charger depuis .env:**
```python
import os
from dotenv import load_dotenv
from database import Database

load_dotenv()

db = Database(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)
```

### Hostnames différents

**Local:**
```python
db = Database(..., host="localhost", port=3306, ...)
```

**Docker compose:**
```python
db = Database(..., host="db", port=3306, ...)  # "db" = nom du service
```

**Docker avec port mappé:**
```python
db = Database(..., host="localhost", port=3307, ...)  # Port externe
```

---

## 📊 Workflow complet

### 1. Setup initial
```python
from database import Database

db = Database(
    user="wpuser",
    password="wppass",
    host="localhost",
    port=3306,
    database="hp_recognition"
)
db.create_tables()  # Créer les tables une fois
```

### 2. Traitement des images
```python
# Pour chaque image du dataset:
image = db.add_image(
    character_name="Harry Potter",
    file_path="/data/harry_001.jpg",
    file_name="harry_001.jpg",
    image_size=102400
)
```

### 3. Extraction des embeddings
```python
# FaceNet extrait l'embedding (128D)
embedding_vector = model.extract_embedding(image_path)

db.add_embedding(
    image_id=image.id,
    character_id=4,
    embedding_vector=embedding_vector
)
```

### 4. Prédiction
```python
# Comparer avec les embeddings existants
predicted_char_id = find_nearest_embedding(embedding_vector)

db.add_prediction(
    image_id=image.id,
    predicted_character_id=predicted_char_id,
    true_character_id=4,
    confidence_score=0.95
)
```

### 5. Statistiques
```python
stats = db.get_global_stats()
accuracy = db.get_character_accuracy()

db.save_execution_log(
    run_id="run_2026_05_22",
    total_images=1000,
    correct_predictions=950,
    total_processing_time_s=120.5,
    avg_inference_time_ms=120.5
)
```
---

**BD prête à l'emploi! 🚀**
