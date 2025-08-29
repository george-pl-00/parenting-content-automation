web: gunicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
worker: celery -A app.tasks worker --loglevel=info --concurrency=2
beat: celery -A app.tasks beat --loglevel=info
