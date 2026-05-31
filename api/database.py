import os
import mysql.connector

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "database"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def save_prediction(character_name: str, confidence: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (character_name, confidence) VALUES (%s, %s)",
        (character_name, confidence)
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