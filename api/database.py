import os
import time
import mysql.connector
from mysql.connector import errors

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "database"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_db_connection(retries: int = 10, delay: int = 5):
    """
    Tente de se connecter à MySQL jusqu'à `retries` fois.
    Attend `delay` secondes entre chaque tentative.
    → Résout le problème de timing au démarrage.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            print(f"✅ DB connected on attempt {attempt}")
            return conn
        except errors.DatabaseError as e:
            last_error = e
            print(f"⏳ DB not ready (attempt {attempt}/{retries}), retrying in {delay}s...")
            time.sleep(delay)
    raise last_error

def save_prediction(character: str, confidence: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (character_name, confidence) VALUES (%s, %s)",
        (character, confidence)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_history(limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, character_name, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows