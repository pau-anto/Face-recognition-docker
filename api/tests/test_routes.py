"""
Tests unitaires pour api/routers/predict.py
Lancer avec : pytest tests/test_routes.py -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────
# Tests du endpoint /health
# ─────────────────────────────────────────────

def test_health_check():
    """Vérifie que l'API répond sur /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ─────────────────────────────────────────────
# Tests du endpoint POST /analyze/
# ─────────────────────────────────────────────

def test_analyze_success():
    """Vérifie que /analyze/ retourne le personnage prédit."""
    ml_response = MagicMock()
    ml_response.status_code = 200
    ml_response.json.return_value = {
        "status": "success",
        "character": "Harry Potter",
        "confidence": 0.95
    }

    with patch("routers.predict.httpx.AsyncClient") as mock_client, \
         patch("routers.predict.save_prediction") as mock_save:

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=ml_response)

        with open("/dev/null", "rb") as f:
            response = client.post(
                "/analyze/",
                files={"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
            )

    # Le résultat doit être retourné
    assert response.status_code == 200
    data = response.json()
    assert data["character"] == "Harry Potter"
    assert data["confidence"] == 0.95


def test_analyze_saves_to_db():
    """Vérifie que la prédiction est bien sauvegardée en base."""
    ml_response = MagicMock()
    ml_response.status_code = 200
    ml_response.json.return_value = {
        "status": "success",
        "character": "Hermione Granger",
        "confidence": 0.88
    }

    with patch("routers.predict.httpx.AsyncClient") as mock_client, \
         patch("routers.predict.save_prediction") as mock_save:

        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=ml_response)

        client.post(
            "/analyze/",
            files={"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        )

        # Vérifie que save_prediction a été appelé avec les bons arguments
        mock_save.assert_called_once_with("Hermione Granger", 0.88)


def test_analyze_ml_service_down():
    """Vérifie que l'API retourne 502 si le ML service est indisponible."""
    ml_response = MagicMock()
    ml_response.status_code = 500

    with patch("routers.predict.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=ml_response)

        response = client.post(
            "/analyze/",
            files={"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        )

    assert response.status_code == 502
    assert "ML service error" in response.json()["detail"]


def test_analyze_no_face_detected():
    """Vérifie que l'API retourne 400 si aucun visage n'est détecté."""
    ml_response = MagicMock()
    ml_response.status_code = 200
    ml_response.json.return_value = {
        "status": "error",
        "message": "No face detected in image"
    }

    with patch("routers.predict.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=ml_response)

        response = client.post(
            "/analyze/",
            files={"file": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        )

    assert response.status_code == 400
    assert "No face detected" in response.json()["detail"]


def test_analyze_missing_file():
    """Vérifie que l'API retourne 422 si aucun fichier n'est envoyé."""
    response = client.post("/analyze/")
    assert response.status_code == 422


# ─────────────────────────────────────────────
# Tests du endpoint GET /analyze/history
# ─────────────────────────────────────────────

def test_history_returns_list():
    """Vérifie que /analyze/history retourne une liste."""
    mock_data = [
        {"id": 1, "character_name": "Harry Potter", "confidence": 0.95, "created_at": "2024-01-01"},
    ]
    with patch("routers.predict.get_history", return_value=mock_data):
        response = client.get("/analyze/history")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_history_empty():
    """Vérifie que /analyze/history retourne [] si la DB est vide."""
    with patch("routers.predict.get_history", return_value=[]):
        response = client.get("/analyze/history")

    assert response.status_code == 200
    assert response.json() == []
