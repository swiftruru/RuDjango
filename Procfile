release: . /app/.venv/bin/activate && python manage.py migrate
web: . /app/.venv/bin/activate && gunicorn --bind 0.0.0.0:${PORT:-8000} RuDjangoProject.wsgi:application
