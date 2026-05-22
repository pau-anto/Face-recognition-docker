#!/bin/sh
# =========================================================
# wait-for-db.sh
# Attend que le container MySQL (db) soit prêt
# avant de lancer l'application Flask.
# =========================================================

HOST="${DB_HOST:-db}"
PORT="${DB_PORT:-3306}"
MAX_RETRIES=30
COUNT=0

echo "⏳ En attente de MySQL sur ${HOST}:${PORT}..."

# Tente une connexion TCP toutes les 2 secondes
until curl -s "telnet://${HOST}:${PORT}" --max-time 1 > /dev/null 2>&1 || \
      (echo > /dev/tcp/${HOST}/${PORT}) > /dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo "❌ MySQL non disponible après ${MAX_RETRIES} tentatives. Abandon."
        exit 1
    fi
    echo "   ... tentative ${COUNT}/${MAX_RETRIES}, nouvelle tentative dans 2s"
    sleep 2
done

echo "✅ MySQL est prêt ! Démarrage de l'application..."
exec "$@"
