"""
Script de test pour Harry Potter Face Recognition Database
Valide que tous les fichiers de BD fonctionnent correctement
"""

import sys
import numpy as np
from database import Database

# Couleurs pour les logs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
END = '\033[0m'


def test_connection():
    """Test 1: Connexion à MySQL"""
    print(f"\n{YELLOW}Test 1: Connexion à MySQL...{END}")
    try:
        db = Database(
            user="root",
            password="",
            host="localhost",
            port=3307,
            database="hp_recognition"
        )
        print(f"{GREEN}Connexion réussie!{END}")
        return db
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return None


def test_create_tables(db):
    """Test 2: Création des tables"""
    print(f"\n{YELLOW}Test 2: Création des tables...{END}")
    try:
        db.create_tables()
        print(f"{GREEN}Tables créées/vérifiées!{END}")
        return True
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def test_get_characters(db):
    """Test 3: Récupération des personnages"""
    print(f"\n{YELLOW}Test 3: Récupération des personnages...{END}")
    try:
        characters = db.get_all_characters()
        print(f"{GREEN}{len(characters)} personnages trouvés:{END}")
        for char in characters[:3]:
            print(f"   - {char['name']} ({char['actor']})")
        if len(characters) > 3:
            print(f"   ... et {len(characters) - 3} autres")
        return True
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def test_add_image(db):
    """Test 4: Ajout d'une image"""
    print(f"\n{YELLOW}Test 4: Ajout d'une image...{END}")
    try:
        image = db.add_image(
            character_name="Harry Potter",
            file_path="/data/test/harry_001.jpg",
            file_name="harry_001.jpg",
            image_size=102400,
            dataset_type="test"
        )
        if image:
            print(f"{GREEN}Image ajoutée (ID: {image.id}){END}")
            return image
        else:
            print(f"{RED}Erreur lors de l'ajout{END}")
            return None
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return None


def test_add_embedding(db, image):
    """Test 5: Ajout d'un embedding"""
    print(f"\n{YELLOW}Test 5: Ajout d'un embedding...{END}")
    try:
        # Créer un vecteur aléatoire 128D (simule FaceNet)
        embedding_vector = np.random.rand(128).astype(np.float32)
        
        emb = db.add_embedding(
            image_id=image.id,
            character_id=4,  # Harry Potter = ID 4
            embedding_vector=embedding_vector,
            processing_time_ms=45
        )
        if emb:
            print(f"{GREEN}Embedding sauvegardé (ID: {emb.id}){END}")
            return True
        else:
            print(f"{RED}Erreur{END}")
            return False
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def test_add_prediction(db, image):
    """Test 6: Ajout d'une prédiction"""
    print(f"\n{YELLOW}Test 6: Ajout d'une prédiction...{END}")
    try:
        pred = db.add_prediction(
            image_id=image.id,
            predicted_character_id=4,  # Prédiction: Harry Potter
            predicted_character_name="Harry Potter",
            true_character_id=4,  # Vrai: Harry Potter (correct!)
            confidence_score=0.95,
            distance=0.25,
            inference_time_ms=120,
            run_id="test_run_2026"
        )
        if pred:
            print(f"{GREEN}Prédiction sauvegardée (ID: {pred.id}){END}")
            print(f"   - Correct: {pred.is_correct}")
            print(f"   - Confiance: {pred.confidence_score:.4f}")
            return True
        else:
            print(f"{RED}Erreur{END}")
            return False
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def test_get_stats(db):
    """Test 7: Récupération des statistiques"""
    print(f"\n{YELLOW}Test 7: Récupération des statistiques...{END}")
    try:
        stats = db.get_global_stats()
        print(f"{GREEN}Statistiques globales:{END}")
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        return True
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def test_get_recent_predictions(db):
    """Test 8: Récupération des prédictions récentes"""
    print(f"\n{YELLOW}Test 8: Récupération des prédictions récentes...{END}")
    try:
        predictions = db.get_recent_predictions(limit=5)
        if predictions:
            print(f"{GREEN}{len(predictions)} prédictions récentes:{END}")
            for p in predictions[:3]:
                print(f"   - ID {p['id']}: {p['confidence']:.4f} confiance")
        else:
            print(f"{YELLOW}Aucune prédiction (normal au premier lancement){END}")
        return True
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
        return False


def main():
    """Lance tous les tests"""
    print("=" * 70)
    print("TESTS BASE DE DONNÉES - Harry Potter Face Recognition")
    print("=" * 70)
    
    # Test 1: Connexion
    db = test_connection()
    if not db:
        print(f"\n{RED}Impossible de continuer sans connexion à la BD{END}")
        sys.exit(1)
    
    # Test 2: Créer les tables
    if not test_create_tables(db):
        print(f"\n{RED}Impossible de continuer sans tables{END}")
        sys.exit(1)
    
    # Test 3: Récupérer les personnages
    test_get_characters(db)
    
    # Test 4: Ajouter une image
    image = test_add_image(db)
    if image:
        # Test 5: Ajouter un embedding
        test_add_embedding(db, image)
        
        # Test 6: Ajouter une prédiction
        test_add_prediction(db, image)
    
    # Test 7: Récupérer les stats
    test_get_stats(db)
    
    # Test 8: Récupérer les prédictions récentes
    test_get_recent_predictions(db)
    
    # Résumé final
    print("\n" + "=" * 70)
    print(f"{GREEN}TOUS LES TESTS SONT TERMINÉS!{END}")
    print("=" * 70)
    print(f"\n{GREEN}Votre BD est prête à l'emploi!{END}\n")


if __name__ == "__main__":
    main()