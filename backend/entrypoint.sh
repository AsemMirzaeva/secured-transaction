
set -e

echo "Waiting for postgres..."
python - << 'PYEOF'
import os, time, psycopg2
for _ in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "secure_pay"),
            user=os.environ.get("POSTGRES_USER", "secure_pay"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
            host=os.environ.get("POSTGRES_HOST", "postgres"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
        ).close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Postgres never became available")
PYEOF

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec daphne -b 0.0.0.0 -p 8000 config.asgi:application