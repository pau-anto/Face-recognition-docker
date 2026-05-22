"""
Database ORM for Harry Potter Face Recognition
Gère toutes les interactions avec MySQL sans écrire de SQL
"""

import json
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


# =========================================================
# 1️⃣ MODÈLES ORM (Classes Python = Tables SQL)
# =========================================================

class Character(Base):
    """Acteurs/Personnages Harry Potter"""
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    actor_name = Column(String(100))
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    images = relationship("Image", back_populates="character", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="character", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Character(id={self.id}, name={self.name}, actor={self.actor_name})>"


class Image(Base):
    """Images du dataset Kaggle"""
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    image_size = Column(Integer)
    dataset_type = Column(String(20), default='train')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    character = relationship("Character", back_populates="images")
    
    def __repr__(self):
        return f"<Image(id={self.id}, file={self.file_name})>"


class Embedding(Base):
    """Vecteurs faciaux 128D extraits par FaceNet"""
    __tablename__ = 'embeddings'
    
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    embedding_vector = Column(LargeBinary, nullable=False)
    embedding_dim = Column(Integer, default=128)
    model_version = Column(String(50), default='facenet-pytorch')
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    character = relationship("Character", back_populates="embeddings")
    
    def set_embedding(self, vector: np.ndarray):
        """Sauvegarde un vecteur numpy en binaire"""
        self.embedding_vector = vector.astype(np.float32).tobytes()
    
    def get_embedding(self) -> np.ndarray:
        """Récupère le vecteur sous forme numpy"""
        return np.frombuffer(self.embedding_vector, dtype=np.float32)
    
    def __repr__(self):
        return f"<Embedding(id={self.id}, dim={self.embedding_dim})>"


class Prediction(Base):
    """Historique complet des prédictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    predicted_character_id = Column(Integer, ForeignKey('characters.id'))
    predicted_character_name = Column(String(100))
    true_character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    confidence_score = Column(Float, nullable=False)
    distance_euclidean = Column(Float)
    is_correct = Column(Boolean, default=None)
    inference_time_ms = Column(Integer)
    model_version = Column(String(50), default='facenet-pytorch')
    run_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, conf={self.confidence_score:.4f}, correct={self.is_correct})>"


class ExecutionLog(Base):
    """Logs d'exécution et statistiques globales"""
    __tablename__ = 'execution_logs'
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(100), nullable=False, unique=True)
    total_images = Column(Integer)
    correct_predictions = Column(Integer)
    accuracy = Column(Float)
    total_processing_time_s = Column(Float)
    avg_inference_time_ms = Column(Float)
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionLog(run_id={self.run_id}, accuracy={self.accuracy}%)>"


# =========================================================
# 2️⃣ CLASSE DATABASE (Interface principale)
# =========================================================

class Database:
    """
    Gestionnaire de BD pour Harry Potter Face Recognition
    
    Usage:
        db = Database(user="wpuser", password="wppass", 
                     host="localhost", port=3306, database="hp_recognition")
        db.create_tables()
        db.add_prediction(image_id=1, ...)
    """
    
    def __init__(self, user: str, password: str, host: str, port: int, database: str):
        """Initialise la connexion à MySQL"""
        self.connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
        self.engine = create_engine(self.connection_string, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"✅ Connecté à {host}:{port}/{database}")
    
    def create_tables(self):
        """Crée toutes les tables (si elles n'existent pas)"""
        Base.metadata.create_all(self.engine)
        logger.info("✅ Tables de la BD créées/vérifiées")
    
    def get_session(self):
        """Retourne une nouvelle session SQLAlchemy"""
        return self.Session()
    
    # =====================================================
    # MÉTHODES: IMAGES
    # =====================================================
    
    def add_image(self, character_name: str, file_path: str, file_name: str, 
                  image_size: int, dataset_type: str = 'train') -> Optional[Image]:
        """Ajoute une image à la BD"""
        session = self.get_session()
        try:
            # Trouver le personnage
            character = session.query(Character).filter_by(name=character_name).first()
            if not character:
                logger.error(f"❌ Personnage '{character_name}' introuvable")
                return None
            
            # Créer l'image
            image = Image(
                character_id=character.id,
                file_path=file_path,
                file_name=file_name,
                image_size=image_size,
                dataset_type=dataset_type
            )
            session.add(image)
            session.commit()
            logger.info(f"✅ Image ajoutée: {file_name}")
            return image
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erreur: {e}")
            return None
        finally:
            session.close()
    
    def get_images_by_character(self, character_name: str) -> List[Image]:
        """Récupère toutes les images d'un personnage"""
        session = self.get_session()
        try:
            images = session.query(Image).join(Character).filter(
                Character.name == character_name
            ).all()
            return images
        finally:
            session.close()
    
    # =====================================================
    # MÉTHODES: EMBEDDINGS
    # =====================================================
    
    def add_embedding(self, image_id: int, character_id: int, 
                     embedding_vector: np.ndarray, processing_time_ms: int = None) -> Optional[Embedding]:
        """Sauvegarde un embedding (vecteur facial 128D)"""
        session = self.get_session()
        try:
            emb = Embedding(
                image_id=image_id,
                character_id=character_id,
                embedding_dim=len(embedding_vector),
                processing_time_ms=processing_time_ms
            )
            emb.set_embedding(embedding_vector)
            session.add(emb)
            session.commit()
            logger.info(f"✅ Embedding sauvegardé pour image {image_id}")
            return emb
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erreur: {e}")
            return None
        finally:
            session.close()
    
    def get_all_embeddings(self, character_name: str = None) -> List[Embedding]:
        """Récupère tous les embeddings (optionnellement filtrés)"""
        session = self.get_session()
        try:
            query = session.query(Embedding)
            if character_name:
                query = query.join(Character).filter(Character.name == character_name)
            return query.all()
        finally:
            session.close()
    
    # =====================================================
    # MÉTHODES: PREDICTIONS
    # =====================================================
    
    def add_prediction(self, image_id: int, predicted_character_id: int, 
                      predicted_character_name: str, true_character_id: int,
                      confidence_score: float, distance: float = None,
                      inference_time_ms: int = None, run_id: str = None) -> Optional[Prediction]:
        """Sauvegarde une prédiction"""
        session = self.get_session()
        try:
            # Vérifier si la prédiction est correcte
            is_correct = (predicted_character_id == true_character_id) if predicted_character_id else False
            
            pred = Prediction(
                image_id=image_id,
                predicted_character_id=predicted_character_id,
                predicted_character_name=predicted_character_name,
                true_character_id=true_character_id,
                confidence_score=confidence_score,
                distance_euclidean=distance,
                is_correct=is_correct,
                inference_time_ms=inference_time_ms,
                run_id=run_id
            )
            session.add(pred)
            session.commit()
            logger.info(f"✅ Prédiction sauvegardée (correcte: {is_correct})")
            return pred
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erreur: {e}")
            return None
        finally:
            session.close()
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict]:
        """Récupère les prédictions récentes (pour interface web)"""
        session = self.get_session()
        try:
            predictions = session.query(Prediction).order_by(
                Prediction.created_at.desc()
            ).limit(limit).all()
            
            result = []
            for p in predictions:
                result.append({
                    'id': p.id,
                    'true_character': p.true_character_id,
                    'predicted_character': p.predicted_character_id or 'Unknown',
                    'confidence': round(p.confidence_score, 4),
                    'is_correct': p.is_correct,
                    'inference_time_ms': p.inference_time_ms,
                    'created_at': p.created_at.isoformat()
                })
            return result
        finally:
            session.close()
    
    # =====================================================
    # MÉTHODES: STATISTIQUES
    # =====================================================
    
    def get_global_stats(self) -> Dict:
        """Récupère les statistiques globales"""
        session = self.get_session()
        try:
            predictions = session.query(Prediction).all()
            if not predictions:
                return {'message': 'Aucune prédiction'}
            
            correct = sum(1 for p in predictions if p.is_correct)
            accuracy = 100 * correct / len(predictions)
            avg_confidence = sum(p.confidence_score for p in predictions) / len(predictions)
            
            return {
                'total_predictions': len(predictions),
                'correct_predictions': correct,
                'accuracy_percent': round(accuracy, 2),
                'avg_confidence': round(avg_confidence, 4)
            }
        finally:
            session.close()
    
    def get_character_accuracy(self) -> Dict:
        """Récupère la précision par personnage"""
        session = self.get_session()
        try:
            characters = session.query(Character).all()
            stats = {}
            
            for char in characters:
                predictions = session.query(Prediction).filter_by(
                    true_character_id=char.id
                ).all()
                
                if predictions:
                    correct = sum(1 for p in predictions if p.is_correct)
                    accuracy = 100 * correct / len(predictions)
                    avg_conf = sum(p.confidence_score for p in predictions) / len(predictions)
                    
                    stats[char.name] = {
                        'total': len(predictions),
                        'correct': correct,
                        'accuracy': round(accuracy, 2),
                        'avg_confidence': round(avg_conf, 4)
                    }
            return stats
        finally:
            session.close()
    
    def get_all_characters(self) -> List[Dict]:
        """Récupère tous les personnages"""
        session = self.get_session()
        try:
            characters = session.query(Character).all()
            return [
                {'id': c.id, 'name': c.name, 'actor': c.actor_name}
                for c in characters
            ]
        finally:
            session.close()
    
    def save_execution_log(self, run_id: str, total_images: int, 
                          correct_predictions: int, total_processing_time_s: float,
                          avg_inference_time_ms: float, notes: str = None) -> Optional[ExecutionLog]:
        """Sauvegarde un log d'exécution"""
        session = self.get_session()
        try:
            accuracy = 100 * correct_predictions / total_images if total_images > 0 else 0
            
            log = ExecutionLog(
                run_id=run_id,
                total_images=total_images,
                correct_predictions=correct_predictions,
                accuracy=accuracy,
                total_processing_time_s=total_processing_time_s,
                avg_inference_time_ms=avg_inference_time_ms,
                notes=notes
            )
            session.add(log)
            session.commit()
            logger.info(f"✅ Log d'exécution sauvegardé: {run_id}")
            return log
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erreur: {e}")
            return None
        finally:
            session.close()
    
    def export_predictions_to_json(self, run_id: str = None, 
                                   output_file: str = None) -> str:
        """Exporte les prédictions en JSON"""
        session = self.get_session()
        try:
            query = session.query(Prediction)
            if run_id:
                query = query.filter_by(run_id=run_id)
            
            predictions = query.all()
            data = []
            
            for p in predictions:
                data.append({
                    'id': p.id,
                    'image_id': p.image_id,
                    'true_character_id': p.true_character_id,
                    'predicted_character_id': p.predicted_character_id,
                    'confidence': float(p.confidence_score),
                    'distance': float(p.distance_euclidean) if p.distance_euclidean else None,
                    'is_correct': p.is_correct,
                    'inference_time_ms': p.inference_time_ms,
                    'created_at': p.created_at.isoformat()
                })
            
            json_str = json.dumps(data, indent=2)
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(json_str)
                logger.info(f"✅ Prédictions exportées vers {output_file}")
            return json_str
        finally:
            session.close()


# =========================================================
# EXEMPLE D'UTILISATION
# =========================================================

if __name__ == "__main__":
    # Connexion à la BD
    db = Database(
        user="wpuser",
        password="wppass",
        host="localhost",
        port=3306,
        database="hp_recognition"
    )
    
    # Créer les tables
    db.create_tables()
    
    # Récupérer les personnages
    characters = db.get_all_characters()
    print(f"✅ {len(characters)} personnages trouvés")
    
    # Récupérer les stats
    stats = db.get_global_stats()
    print(f"Stats: {stats}")