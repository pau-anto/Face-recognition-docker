import pickle
import json
import io
import torch
import numpy as np
from fastapi import FastAPI, UploadFile, File
from PIL import Image
from facenet_pytorch import MTCNN
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


app = FastAPI(title="Harry Potter Face Recognition ML Service")

# ---------- Configuration ----------
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/harry_model.pkl")
METADATA_PATH = os.getenv("METADATA_PATH", "/app/model/metadata.json")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------- Chargement du modèle ----------
print("Loading model...")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
model = model.to(DEVICE)
model.eval()
print(f"Model loaded on {DEVICE}")

# ---------- Chargement des classes ----------
with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)
classes = metadata["classes"]          # ex: ["Harry Potter", "Hermione Granger", ...]
idx_to_class = {i: cls for i, cls in enumerate(classes)}
print(f"Classes: {classes}")

# ---------- Initialisation de MTCNN ----------
mtcnn = MTCNN(image_size=160, margin=20, post_process=True, keep_all=False, device=DEVICE)

# ---------- Prétraitement ----------
def preprocess_face(image_bytes: bytes):
    """Détecte le visage, recadre, redimensionne à 160x160, normalise."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    face = mtcnn(img)
    if face is None:
        return None
    # face est un tenseur (3, 160, 160) déjà normalisé entre 0 et 1 ?
    # D'après ta cellule : (face - 0.5) / 0.5
    face = (face - 0.5) / 0.5
    face = face.unsqueeze(0)  # ajoute dimension batch
    return face.to(DEVICE)

# ---------- Route de prédiction ----------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        face_tensor = preprocess_face(image_bytes)
        if face_tensor is None:
            return {"status": "error", "message": "No face detected in image"}
        
        with torch.no_grad():
            logits = model(face_tensor)
            probs = torch.softmax(logits, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_idx].item()
        
        character = idx_to_class[pred_idx]
        return {
            "status": "success",
            "character": character,
            "confidence": confidence
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health():
    return {"status": "alive"}