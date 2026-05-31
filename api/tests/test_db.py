"""
Tests unitaires pour api/database.py
Lancer avec : pytest tests/test_db.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import save_prediction, get_history, get_db_connection


# ─────────────────────────────────────────────
# Tests de connexion
# ─────────────────────────────────────────────

def test_db_config_uses_env_variables():
    """Vérifie que la config DB lit bien les variables d'environnement."""
    with patch.dict(os.environ, {
        "DB_HOST": "myhost",
        "DB_USER": "myuser",
        "DB_PASSWORD": "mypass",
        "DB_NAME": "mydb"
    }):
        import importlib
        import database
        importlib.reload(database)
        assert database.DB_CONFIG["host"] == "myhost"
        assert database.DB_CONFIG["user"] == "myuser"
        assert database.DB_CONFIG["database"] == "mydb"


def test_get_db_connection_fails_gracefully():
    """Vérifie qu'une mauvaise config lève une exception claire."""
    with patch("database.mysql.connector.connect") as mock_connect:
        mock_connect.side_effect = Exception("Connection refused")
        with pytest.raises(Exception, match="Connection refused"):
            get_db_connection()


# ─────────────────────────────────────────────
# Tests de save_prediction
# ─────────────────────────────────────────────

def test_save_prediction_calls_insert():
    """Vérifie que save_prediction exécute bien un INSERT."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        save_prediction("Harry Potter", 0.95)

    # Vérifie que execute a été appelé
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]

    # Vérifie que le SQL contient INSERT
    assert "INSERT" in call_args[0].upper()
    # Vérifie que les valeurs sont correctes
    assert call_args[1] == ("Harry Potter", 0.95)


def test_save_prediction_commits():
    """Vérifie que save_prediction fait bien un commit."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        save_prediction("Hermione Granger", 0.88)

    mock_conn.commit.assert_called_once()


def test_save_prediction_closes_connection():
    """Vérifie que la connexion est bien fermée après l'insertion."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        save_prediction("Ron Weasley", 0.72)

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_save_prediction_db_error_raises():
    """Vérifie qu'une erreur DB remonte correctement."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("DB Error")
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        with pytest.raises(Exception, match="DB Error"):
            save_prediction("Draco Malfoy", 0.60)


# ─────────────────────────────────────────────
# Tests de get_history
# ─────────────────────────────────────────────

def test_get_history_returns_list():
    """Vérifie que get_history retourne une liste."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "character_name": "Harry Potter", "confidence": 0.95, "created_at": "2024-01-01"},
        {"id": 2, "character_name": "Hermione Granger", "confidence": 0.88, "created_at": "2024-01-02"},
    ]
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        result = get_history(limit=10)

    assert isinstance(result, list)
    assert len(result) == 2


def test_get_history_uses_limit():
    """Vérifie que get_history passe bien le paramètre limit au SQL."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        get_history(limit=5)

    call_args = mock_cursor.execute.call_args[0]
    assert call_args[1] == (5,)


def test_get_history_empty_db():
    """Vérifie que get_history retourne [] si la DB est vide."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor

    with patch("database.get_db_connection", return_value=mock_conn):
        result = get_history()

    assert result == []
