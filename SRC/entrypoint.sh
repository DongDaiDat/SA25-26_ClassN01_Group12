#!/usr/bin/env sh
set -e

# Đợi Postgres sẵn sàng
python - <<'PY'
import os, time, psycopg2
host=os.getenv("POSTGRES_HOST","unimis_db")
port=int(os.getenv("POSTGRES_PORT","5432"))
user=os.getenv("POSTGRES_USER","unimis")
password=os.getenv("POSTGRES_PASSWORD","unimis")
dbname=os.getenv("POSTGRES_DB","unimis")
for i in range(60):
    try:
        conn=psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
        conn.close()
        print("DB is ready")
        break
    except Exception as e:
        print("Waiting for DB...", e)
        time.sleep(2)
else:
    raise SystemExit("DB not ready after 120s")
PY

# migrate DB
python manage.py makemigrations miscore --noinput || true
python manage.py migrate --noinput

# chạy dev server
python manage.py runserver ${DJANGO_HOST:-0.0.0.0}:${DJANGO_PORT:-8000}
